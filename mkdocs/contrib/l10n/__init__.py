# coding: utf-8

from __future__ import absolute_import, unicode_literals

import os
import logging
from babel.support import Translations, NullTranslations
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.structure.files import Files

log = logging.getLogger(__name__)
base_path = os.path.dirname(os.path.abspath(__file__))


class LocalizationPlugin(BasePlugin):
    """ Add localization feature to MkDocs. """

    LOCALES_DIR = 'locales'

    config_scheme = (
        ('locales', config_options.Type(list, default=['en'])),
    )

    def on_env(self, env, config, **kwargs):
        translations = self._get_merged_translations(config['theme'].dirs)
        if translations is None:
            raise Exception('Expected translations but none found.')

        env.add_extension('jinja2.ext.i18n')
        env.install_gettext_translations(translations)
        return env

    def _get_merged_translations(self, theme_dirs):
        merged_translations = None

        for theme_dir in reversed(theme_dirs):
            dirname = os.path.join(theme_dir, self.LOCALES_DIR)
            translations = Translations.load(dirname, self.config['locales'])

            if type(translations) is NullTranslations:
                log.debug('No translations found here: \'{}\''.format(dirname))
                continue

            log.debug('Translations found here: \'{}\''.format(dirname))
            if merged_translations is None:
                merged_translations = translations
            else:
                merged_translations.merge(translations)

        return merged_translations

    def on_files(self, files, **kwargs):
        def is_translation_file(file):
            return file.src_path.endswith(('.pot', '.po', '.mo'))

        return Files(list(filter(lambda file: not is_translation_file(file), files)))
