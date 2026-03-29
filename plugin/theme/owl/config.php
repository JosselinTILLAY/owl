<?php
defined('MOODLE_INTERNAL') || die();

$THEME->name = 'owl';
$THEME->parents = ['boost'];

$THEME->sheets = [];
$THEME->editor_sheets = [];
$THEME->usefallback = true;
$THEME->enable_dock = false;
$THEME->yuicssmodules = [];
$THEME->rendererfactory = 'theme_overridden_renderer_factory';
$THEME->requiredblocks = '';
$THEME->addblockposition = BLOCK_ADDBLOCK_POSITION_FLATNAV;
$THEME->haseditswitch = true;
$THEME->usescourseindex = true;

$THEME->scss = function($theme) {
    return theme_owl_get_main_scss_content($theme);
};

$THEME->prescsscallback = 'theme_owl_get_pre_scss';
$THEME->extrascsscallback = 'theme_owl_get_extra_scss';
