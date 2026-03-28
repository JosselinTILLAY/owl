<?php
defined('MOODLE_INTERNAL') || die();

require_once(__DIR__ . '/locallib.php');

function owl_add_instance($data, $mform = null) {
    global $DB;

    // Nom par défaut si le prof n'a rien saisi
    if (empty(trim($data->name))) {
        $typenames = [
            'podcast' => get_string('type_podcast', 'mod_owl'),
            'video'   => get_string('type_video',   'mod_owl'),
            'qcm'     => get_string('type_qcm',     'mod_owl'),
        ];
        $data->name = $typenames[$data->type] ?? ucfirst($data->type);
    }

    $data->timecreated  = time();
    $data->timemodified = time();
    $data->status       = 'pending';

    $instanceid = $DB->insert_record('owl', $data);

    if ($mform) {
        $context = context_module::instance($data->coursemodule);
        file_save_draft_area_files(
            $data->documents,
            $context->id,
            'mod_owl',
            'documents',
            $instanceid,
            ['subdirs' => 0, 'maxfiles' => 20]
        );

        $task = new \mod_owl\task\upload_pdfs();
        $task->set_custom_data(['instanceid' => $instanceid, 'contextid' => $context->id]);
        \core\task\manager::queue_adhoc_task($task);
    }

    return $instanceid;
}

function owl_update_instance($data, $mform = null) {
    global $DB;

    $data->timemodified = time();
    $data->id = $data->instance;

    $result = $DB->update_record('owl', $data);

    if ($mform) {
        $context = context_module::instance($data->coursemodule);
        file_save_draft_area_files(
            $data->documents,
            $context->id,
            'mod_owl',
            'documents',
            $data->id,
            ['subdirs' => 0, 'maxfiles' => 20]
        );

        $task = new \mod_owl\task\upload_pdfs();
        $task->set_custom_data(['instanceid' => $data->id, 'contextid' => $context->id]);
        \core\task\manager::queue_adhoc_task($task);
    }

    return $result;
}

function owl_delete_instance($id) {
    global $DB;

    if (!$instance = $DB->get_record('owl', ['id' => $id])) {
        return false;
    }

    $DB->delete_records('owl', ['id' => $id]);

    return true;
}

function owl_supports($feature) {
    switch ($feature) {
        case FEATURE_MOD_INTRO:
            return true;
        case FEATURE_BACKUP_MOODLE2:
            return false;
        default:
            return null;
    }
}
