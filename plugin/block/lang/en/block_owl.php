<?php
defined('MOODLE_INTERNAL') || die();

$string['pluginname']        = 'Owl';
$string['owl:addinstance']   = 'Ajouter un bloc Owl';
$string['owl:myaddinstance'] = 'Ajouter Owl au tableau de bord';

// Paramètres d'administration
$string['settings_enabled']      = 'Activer le bloc Owl';
$string['settings_enabled_desc'] = 'Si désactivé, le bloc n\'affiche aucun contenu sur toutes les pages.';

// Commun
$string['settings_provider_none'] = 'Aucun';
$string['settings_apikey_desc']   = 'Clé API pour le provider sélectionné.';

// Podcast
$string['settings_podcast_heading']      = 'Podcast';
$string['settings_podcast_provider']     = 'Provider';
$string['settings_podcast_provider_desc'] = 'Fournisseur IA utilisé pour la génération de podcasts.';
$string['settings_podcast_apikey']       = 'Clé API';

// Vidéo
$string['settings_video_heading']      = 'Vidéo';
$string['settings_video_provider']     = 'Provider';
$string['settings_video_provider_desc'] = 'Fournisseur IA utilisé pour la génération de vidéos.';
$string['settings_video_apikey']       = 'Clé API';

// QCM
$string['settings_qcm_heading']      = 'QCM';
$string['settings_qcm_provider']     = 'Provider';
$string['settings_qcm_provider_desc'] = 'Fournisseur IA utilisé pour la génération de QCM.';
$string['settings_qcm_apikey']       = 'Clé API';

// Formulaire de génération
$string['form_type']           = 'Type de génération';
$string['type_podcast']        = 'Podcast';
$string['type_video']          = 'Vidéo';
$string['type_qcm']            = 'QCM';
$string['form_section']        = 'Topic cible';
$string['form_prompt']         = 'Prompt (optionnel)';
$string['form_prompt_help']    = 'Décrivez ce que vous souhaitez générer, les points à couvrir, le ton, le public cible, etc.';
$string['form_documents']      = 'Documents sources';
$string['form_documents_hint'] = 'Maintenez Ctrl (ou Cmd) pour sélectionner plusieurs documents.';
$string['no_documents']        = 'Aucun document disponible dans ce cours.';
$string['form_submit']         = 'Générer';
$string['generate_success']    = 'Génération lancée avec succès.';

// Page d'attente
$string['pending_title']   = 'Génération en cours';
$string['pending_heading'] = 'Génération en cours...';
$string['pending_message'] = 'Votre contenu est en cours de génération. Cela peut prendre quelques minutes.';
$string['pending_hint']    = 'Le contenu sera automatiquement ajouté à votre cours dès qu\'il sera prêt. Vous pouvez retourner à votre cours et continuer à travailler normalement.';
$string['pending_back']    = 'Retourner au cours';