<?php
defined('MOODLE_INTERNAL') || die();

if ($ADMIN->fulltree) {
    $settings = new admin_settingpage('theme_owl', get_string('configtitle', 'theme_owl'));

    // Pour le moment, pas de settings custom.
    // On pourra ajouter : logo, couleur primaire, background image, etc.

    $page = $settings;
}
