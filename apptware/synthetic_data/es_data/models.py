from elasticsearch_dsl import (
    Document, Keyword, Boolean, Date, Integer, Text, Float, Long, Double, Nested,
    InnerDoc
)


class Ann(Document):
    """Mapping for the ann index documents."""
    ann_id = Keyword()
    update_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    add_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    event_trigger = Keyword()
    last_annotator = Keyword()
    last_annotator_date = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')  # Check UTC ?
    note_length = Integer(index=False)
    sentence_char_start = Integer(index=False)
    sentence_char_end = Integer(index=False)
    note_type = Keyword()
    note_type_raw = Keyword()
    note_id = Keyword()
    note_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    char_start = Integer(index=False)
    char_end = Integer(index=False)
    note_provider_type = Keyword()
    note_provider_service = Keyword()
    case_id = Keyword()
    patient_id = Keyword()
    encounter_id = Keyword()
    enterprise_patient_id = Keyword()
    hospital = Keyword()
    snippet_text = Text(fields={'raw': Keyword()})
    label_type = Keyword()
    snippet_sentence = Text(fields={'raw': Keyword()})
    comment_text = Text(fields={'raw': Keyword()})
    snippet_label = Keyword()
    user_response_type = Keyword()
    code_umls = Keyword()
    code_snomed = Keyword()
    code_rxnorm = Keyword()
    code_loinc = Keyword()
    attribute_hypothetical = Keyword()
    attribute_bodysite = Keyword()
    attribute_possible = Keyword()
    attribute_negation = Keyword()
    attribute_section = Keyword()
    attribute_value = Keyword()
    attribute_value_num = Float(index=False)
    attribute_value_units = Keyword()
    snippet_source = Keyword()
    snippet_entropy = Float(index=False)
    machine_type = Keyword()
    model_id = Keyword()
    kermit_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    kermit_label = Keyword()
    similarity_group = Keyword()
    CRF_probability = Float(index=False)
    kermit_probability = Float(index=False)
    duplicate_status = Keyword()
    concept_probability = Float(index=False)
    sentence_probability = Float(index=False)

    class Index:
        name = "ann"


class PredictionsDischargeProbability(InnerDoc):
    date_time = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    value = Float()


class Relos(Document):
    """Mapping for Relos Index Documents."""
    acrr_evaluation_date = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    acrr_rating = Keyword()
    acrr_score = Float()
    whitecoat_chartreview_url = Keyword()
    add_source = Keyword()
    admission_diagnosis_text = Keyword()
    admission_type = Keyword()
    admission_diagnosis = Keyword()
    admit_source = Keyword()
    age = Integer()
    age_group = Keyword()
    attending_doctor_id = Keyword()
    attending_doctor_name = Keyword()
    bed = Keyword()
    benefit_plan_name = Keyword()
    case_activity_status = Keyword()
    case_entropy = Float()
    case_id = Keyword()
    current_hours_of_stay = Integer()
    current_reviewer = Keyword()
    date_of_add_instance = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    date_of_admission = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    date_of_death = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    date_of_discharge = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    date_of_point_of_care_effective = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    date_of_update_instance = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    death_ind = Keyword()
    department_abbreviation = Keyword()
    department_name = Keyword()
    diagnosis_this_visit = Keyword()
    discharge_location = Keyword()
    discharge_probability = Float()
    discharge_probability_24hr = Float()
    discharge_probability_48hr = Float()
    discharge_probability_72hr = Float()

    discharge_status = Keyword()
    encounter_id = Keyword()
    financial_class = Keyword()
    first_name = Keyword()
    gender = Keyword()
    hospital = Keyword()
    hospital_account = Keyword()
    hospital_service = Keyword()
    intervention_categories = Keyword()
    language = Keyword()
    last_name = Keyword()

    last_confidence = Long()

    last_decision = Keyword()
    last_decision_comment = Keyword()

    last_decision_duration_in_sec = Integer()

    last_decision_maker = Keyword()

    last_review_decision_time = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    last_review_start_time = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')

    latest_complexity_index = Double()
    latest_confidence = Long()

    latest_decision = Keyword()

    latest_decision_comment = Keyword()

    latest_decision_maker = Keyword()

    latest_review_decision_time = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    latest_review_start_time = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')

    latest_review_status = Keyword()
    length_of_stay = Integer()
    marital_status = Keyword()
    middle_name = Keyword()

    patient_class = Keyword()
    patient_locations = Keyword()

    patient_type = Keyword()
    patient_id = Keyword()

    point_of_care = Keyword()

    predictions_discharge_probability = Nested(PredictionsDischargeProbability)

    prelos = Keyword()
    prev_discharge_probabilities = Float()

    prev_discharge_probability_24hr = Float()
    prev_discharge_probability_48hr = Float()
    prev_discharge_probability_72hr = Float()

    prev_prelos = Keyword()
    prev_rlos = Float()

    primary_admission_diagnosis = Keyword()

    # Definition of field - raw and regular fields, combines the multiple fields into a single field.
    primary_icd10 = Keyword(fields={"analyzed": Keyword()})
    # primary_icd10_analyzed = Keyword()

    prior_bed = Keyword()
    prior_point_of_care = Keyword()
    prior_room = Keyword()

    race = Keyword()
    reason_for_visit = Keyword()
    rlos = Float()
    room = Keyword()
    secondary_icd10 = Keyword()
    secondary_icd10_analyzed = Keyword()

    # TODO: GROT. Is in use right now
    service_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    service_date_history = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    treatment_teams = Keyword()
    update_source = Keyword()
    user_confidence = Long()

    class Index:
        name = "relos"

    def to_dict(self, include_meta=False, skip_empty=True):
        self.meta.id = self.case_id
        return super(Relos, self).to_dict(include_meta=include_meta, skip_empty=skip_empty)


class RelosAnn(Document):
    """Mapping for Relos Ann Index Documents."""
    case_id = Keyword()
    review_action = Keyword()
    review_action_time = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    review_comment = Keyword()
    review_confidence = Long()
    review_duration_in_sec = Integer()
    review_mode = Keyword()
    reviewer = Keyword()

    class Index:
        name = "relos-ann"
