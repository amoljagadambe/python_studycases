from elasticsearch_dsl import (
    Document, Keyword, Boolean, Date, Integer, Text, Float, Long, Double, Nested,
    InnerDoc
)


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

    service_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    service_date_history = Date(
        format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    treatment_teams = Keyword()
    update_source = Keyword()
    user_confidence = Long()

    def to_dict(self, include_meta=False, skip_empty=True):
        self.meta.id = self.case_id
        return super(Relos, self).to_dict(include_meta=include_meta, skip_empty=skip_empty)


class Note(Document):
    """Mapping for note Index Documents."""
    case_id = Keyword()
    de_id = Boolean()
    hospital = Keyword()
    patient_id = Keyword()
    encounter_id = Keyword()
    enterprise_patient_id = Keyword()
    note_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    note_id = Keyword()
    note_length = Integer()
    note_type = Keyword()
    note_type_raw = Keyword()
    note_provider_id = Keyword()
    note_provider_service = Keyword()
    note_provider_type = Keyword()
    note_provider_name = Keyword(multi=True)
    update_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    add_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    ds_add_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    ds_update_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    sentence_offsets = Integer(multi=True, index=False)
    text = Text()
    raw_text = Text()
    sentences = Text(multi=True)
    token_offsets = Integer(multi=True, index=False)

    def to_dict(self, include_meta=False, skip_empty=True):
        self.meta.id = "{}_{}".format(self.case_id, self.note_id)
        return super(Note, self).to_dict(include_meta=include_meta, skip_empty=skip_empty)
