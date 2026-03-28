<?php
defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/formslib.php');

class block_owl_generate_form extends moodleform {

    public function definition() {
        $mform = $this->_form;

        // Sélecteur de type
        $types = [
            'podcast' => get_string('type_podcast', 'block_owl'),
            'video'   => get_string('type_video',   'block_owl'),
            'qcm'     => get_string('type_qcm',     'block_owl'),
        ];
        $mform->addElement('select', 'type', get_string('form_type', 'block_owl'), $types);
        $mform->setDefault('type', 'podcast');

        // Sélecteur de topic (section du cours)
        $sections = $this->_customdata['sections'] ?? [];
        $mform->addElement('select', 'sectionid', get_string('form_section', 'block_owl'), $sections);
        $mform->addRule('sectionid', null, 'required');

        // Prompt utilisateur
        $mform->addElement('textarea', 'prompt', get_string('form_prompt', 'block_owl'), ['rows' => 4, 'cols' => 60]);
        $mform->setType('prompt', PARAM_TEXT);
        $mform->addHelpButton('prompt', 'form_prompt', 'block_owl');

        // Ressources existantes du cours (pages, fichiers, labels, etc.)
        $course_resources = $this->_customdata['course_resources'] ?? [];
        if (!empty($course_resources)) {
            $mform->addElement(
                'autocomplete',
                'course_resources',
                get_string('form_course_resources', 'block_owl'),
                $course_resources,
                ['multiple' => true, 'noselectionstring' => get_string('form_course_resources_none', 'block_owl')]
            );
        }

        // Sélection de fichiers via le file picker Moodle
        $options = [
            'subdirs'        => 0,
            'maxfiles'       => 20,
            'accepted_types' => ['.pdf', '.doc', '.docx', '.txt', '.ppt', '.pptx', '.odt', '.odp'],
        ];
        $mform->addElement('filemanager', 'documents', get_string('form_documents', 'block_owl'), null, $options);

        // Champ caché : id du cours
        $mform->addElement('hidden', 'courseid');
        $mform->setType('courseid', PARAM_INT);

        $this->add_action_buttons(true, get_string('form_submit', 'block_owl'));
    }

    public function validation($data, $files) {
        $errors = parent::validation($data, $files);

        $hasresources = !empty($data['course_resources']);
        // Le draftitemid vaut 0 si aucun fichier n'a été uploadé
        $hasdocs = !empty($data['documents']) && $data['documents'] != 0;

        if (!$hasresources && !$hasdocs) {
            $errors['documents'] = get_string('form_sources_required', 'block_owl');
        }

        return $errors;
    }
}
