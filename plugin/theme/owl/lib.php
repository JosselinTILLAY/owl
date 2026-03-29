<?php
defined('MOODLE_INTERNAL') || die();

/**
 * Retourne le contenu SCSS principal du thème Owl.
 */
function theme_owl_get_main_scss_content($theme) {
    global $CFG;

    $preset = file_get_contents($CFG->dirroot . '/theme/boost/scss/preset/default.scss');

    $owl_scss = '';
    $owl_file = $CFG->dirroot . '/theme/owl/scss/owl.scss';
    if (file_exists($owl_file)) {
        $owl_scss = file_get_contents($owl_file);
    }

    return $preset . "\n" . $owl_scss;
}

/**
 * Variables SCSS — même palette que Boost, modernisée.
 */
function theme_owl_get_pre_scss($theme) {
    $scss = '';

    // Palette charte OWL
    $scss .= '$primary: #F07E16;' . "\n";         // Orange OWL
    $scss .= '$secondary: #1B3D2F;' . "\n";       // Vert foncé OWL
    $scss .= '$success: #2A5E47;' . "\n";          // Vert intermédiaire
    $scss .= '$info: #008196;' . "\n";
    $scss .= '$warning: #F5C842;' . "\n";
    $scss .= '$danger: #D94040;' . "\n";

    // Fonts charte OWL
    $scss .= '$font-family-sans-serif: "DM Sans", "Inter", -apple-system, BlinkMacSystemFont, sans-serif;' . "\n";
    $scss .= '$headings-font-family: "Syne", "Barlow Condensed", sans-serif;' . "\n";

    // Body
    $scss .= '$body-bg: #FAFAF8;' . "\n";
    $scss .= '$body-color: #3D3D3D;' . "\n";

    // Border radius global plus doux
    $scss .= '$border-radius: 0.5rem;' . "\n";
    $scss .= '$border-radius-lg: 0.75rem;' . "\n";
    $scss .= '$border-radius-sm: 0.375rem;' . "\n";

    return $scss;
}

/**
 * SCSS supplémentaire.
 */
function theme_owl_get_extra_scss($theme) {
    return '';
}

/**
 * Sert les fichiers du thème.
 */
function theme_owl_pluginfile($course, $cm, $context, $filearea, $args, $forcedownload, array $options = []) {
    if ($context->contextlevel == CONTEXT_SYSTEM) {
        $theme = theme_config::load('owl');
        return $theme->setting_file_serve($filearea, $args, $forcedownload, $options);
    }
    send_file_not_found();
}

/**
 * Injecte le favicon OWL + la font Outfit.
 */
function theme_owl_before_standard_html_head() {
    global $CFG;
    $faviconurl = $CFG->wwwroot . '/theme/owl/pix/favicon.png';
    return '<link rel="icon" type="image/png" href="' . $faviconurl . '">' . "\n" .
           '<link rel="shortcut icon" href="' . $faviconurl . '">' . "\n" .
           '<link rel="preconnect" href="https://fonts.googleapis.com">' . "\n" .
           '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' . "\n" .
           '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Syne:wght@500;600;700;800&display=swap" rel="stylesheet">';
}
