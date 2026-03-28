<?php
// Le nom de la classe DOIT correspondre exactement au nom du fichier.
// Convention Moodle : block_<nom_du_dossier>
class block_owl extends block_base {

    // Initialisation du bloc : définit son titre affiché dans l'interface.
    public function init() {
        $this->title = get_string('pluginname', 'block_owl');
    }

    // Contenu HTML affiché dans le bloc.
    // Doit retourner un objet stdClass avec une propriété 'text'.
    public function get_content() {
        if ($this->content !== null) {
            return $this->content;
        }

        $this->content = new stdClass();
        $this->content->text = html_writer::tag('p', 'Hello Owl ! 🦉');
        $this->content->footer = '';

        return $this->content;
    }

    // Sur quels types de pages ce bloc peut-il apparaître ?
    // 'course-view-*' = toutes les pages de cours (format topics, weeks, etc.)
    public function applicable_formats() {
        return [
            'course-view' => true,  // pages de cours ✅
            'site'        => true,  // page d'accueil ✅
            'my'          => false, // tableau de bord ❌
        ];
    }
}