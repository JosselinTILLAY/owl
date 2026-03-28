<?php
defined('MOODLE_INTERNAL') || die();

function xmldb_owl_upgrade($oldversion) {
    global $DB;
    $dbman = $DB->get_manager();

    if ($oldversion < 2024010102) {
        $table = new xmldb_table('owl');
        $field = new xmldb_field('extracted_text', XMLDB_TYPE_TEXT, null, null, null, null, null, 'status');

        if (!$dbman->field_exists($table, $field)) {
            $dbman->add_field($table, $field);
        }

        upgrade_mod_savepoint(true, 2024010102, 'owl');
    }

    return true;
}
