from datetime import datetime

from faker import Faker
from faker.generator import random
from supabase.client import Client

SUPABASE_URL: str = "https://wmcfvioqoxwwkzzlemes.supabase.co"
SUPABASE_SERVICE_CLIENT_ROLE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndtY2Z2aW9xb3h3d2t6emxlbWVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxOTI2NDQ5MywiZXhwIjoyMDM0ODQwNDkzfQ.4hWpejasbMHB-cEO6zhgmb-Q39qO8ExP02aigOYN9xg"

supabase_faker: Client = Client(SUPABASE_URL, SUPABASE_SERVICE_CLIENT_ROLE_KEY)

fake = Faker()
#
for _ in range(50):
    start_date = datetime(2024, 7, 1)
    end_date = datetime(2024, 7, 31, 23, 59, 59, 999999)

    random_datetime = fake.date_time_between(start_date=start_date, end_date=end_date)

    formatted_datetime = random_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
    first_name = fake.first_name()
    last_name = fake.last_name()
    patient_age = random.randint(0, 100)
    patient_age_unit = random.choice(['days', 'months', 'years'])
    patient_gender = random.choice(['Male', 'Female'])
    patient_address = fake.address().replace('\n', ', ')
    patient_phone_number = fake.phone_number()
    emergency_contact_name = fake.name() if random.choice([True, False]) else None
    emergency_contact_phone = fake.phone_number() if emergency_contact_name else None
    patient_email = fake.email() if random.choice([True, False]) else None
    insurance_provider = fake.company() if random.choice([True, False]) else None
    insurance_policy_number = fake.uuid4() if insurance_provider else None
    coverage_percentage = round(random.uniform(0, 100), 2) if insurance_provider else None
    medical_history = fake.text() if random.choice([True, False]) else None
    allergies = fake.word() if random.choice([True, False]) else None
    current_medications = fake.word() if random.choice([True, False]) else None
    next_visit_date = fake.future_date() if random.choice([True, False]) else None
    patient_clinical_data = fake.text() if random.choice([True, False]) else None
    treatment_plan = fake.text() if random.choice([True, False]) else None
    notes = fake.text() if random.choice([True, False]) else None
    national_id_number = fake.ssn()

    data = supabase_faker.table('patients').insert({
        "national_id_number": national_id_number,
        "first_name": first_name,
        "last_name": last_name,
        "patient_age": patient_age,
        "patient_age_unit": patient_age_unit,
        "patient_gender": patient_gender,
        "patient_address": patient_address,
        "patient_phone_number": patient_phone_number,
        "patient_email": patient_email,
        "insurance_provider": insurance_provider,
        "insurance_policy_number": insurance_policy_number,
        "coverage_percentage": coverage_percentage,
        "notes": notes,
        'created_at': formatted_datetime
    }).execute()

# for _ in range(10):
    #     first_name = fake.first_name()
    #     last_name = fake.last_name()
    #     patient_age = random.randint(0, 100)
    #     patient_age_unit = random.choice(['days', 'months', 'years'])
    #     user_role = random.choice(
    #         ['Secretary', 'Report Writer', 'Admin', 'Doctor', 'Nurse', 'Assistant', 'Clinic Manager', 'Billing Specialist',
    #          'Receptionist', 'IT Support', 'Medical Records Officer', 'Quality Assurance Officer', 'Data Analyst'])
    #     permission_id = random.choice([1, 2, 3, 6, 7, 8, 9, 10, 11])
    #     patient_address = fake.address().replace('\n', ', ')
    #     patient_phone_number = fake.phone_number()
    #     emergency_contact_name = fake.name() if random.choice([True, False]) else None
    #     emergency_contact_phone = fake.phone_number() if emergency_contact_name else None
    #     patient_email = fake.email() if random.choice([True, False]) else None
    # random_doctor_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
    #     # service = random.choice([
    #     #     'Blood Test',
    #     #     'X-Ray',
    #     #     'MRI Scan',
    #     #     'CT Scan',
    #     #     'Physical Therapy',
    #     #     'Vaccination',
    #     #     'Dental Cleaning',
    #     #     'Root Canal Treatment',
    #     #     'Flu Shot',
    #     #     'Cardiology Consultation',
    #     #     'Orthopedic Surgery',
    #     #     'Eye Exam',
    #     #     'Skin Biopsy',
    #     #     'Prenatal Checkup',
    #     #     'Chiropractic Adjustment',
    #     #     'Dietary Consultation',
    #     #     'Hearing Test',
    #     #     'Allergy Testing'
    #     # ])
    #     # insurance_provider = fake.company() if random.choice([True, False]) else None
    #     # insurance_policy_number = fake.uuid4() if insurance_provider else None
    #     # coverage_percentage = round(random.uniform(0, 100), 2) if insurance_provider else None
    #     # medical_history = fake.text() if random.choice([True, False]) else None
    #     # allergies = fake.word() if random.choice([True, False]) else None
    #     # current_medications = fake.word() if random.choice([True, False]) else None
    #     # next_visit_date = fake.future_date() if random.choice([True, False]) else None
    #     # patient_clinical_data = fake.text() if random.choice([True, False]) else None
    #     # treatment_plan = fake.text() if random.choice([True, False]) else None
    #     # notes = fake.text() if random.choice([True, False]) else None
    #     # national_id_number = fake.ssn()
    #     # reportFields = random.choice([
    #     #     "Ultrasound",
    #     #     "X-Ray",
    #     #     "CT Scan",
    #     #     "PET Scan",
    #     #     "Fluoroscopy",
    #     #     "Bone Density Scan (DEXA)",
    #     #     "Echocardiogram",
    #     #     "Electrocardiogram (ECG/EKG)",
    #     #     "Holter Monitor Report",
    #     #     "Cardiac Catheterization",
    #     #     "Biopsy Report",
    #     #     "Histopathology Report",
    #     #     "Cytology Report",
    #     #     "Autopsy Report",
    #     #     "Blood Test",
    #     #     "Urinalysis",
    #     #     "Stool Test",
    #     #     "Liver Function Test",
    #     #     "Kidney Function Test",
    #     #     "Thyroid Function Test",
    #     #     "Pulmonary Function Test (PFT)",
    #     #     "Chest X-Ray",
    #     #     "Sleep Study (Polysomnography)",
    #     #     "Bronchoscopy Report",
    #     #     "Colonoscopy Report",
    #     #     "Capsule Endoscopy Report",
    #     #     "ERCP (Endoscopic Retrograde Cholangiopancreatography) Report",
    #     #     "EMG (Electromyography)",
    #     #     "Spinal Tap (Lumbar Puncture)",
    #     #     "Eye Exam Report",
    #     #     "Optical Coherence Tomography (OCT)",
    #     #     "Retinal Imaging Report",
    #     #     "Prenatal Ultrasound",
    #     #     "Pap Smear",
    #     #     "Pelvic Ultrasound",
    #     #     "Fetal Monitoring Report",
    #     #     "Cancer Staging Report",
    #     #     "Radiation Therapy Report",
    #     #     "Chemotherapy Report"
    #     # ])
    #
    #     # specialty = fake.job()  # Random job title as a specialty
    #     # qualifications = fake.text(max_nb_chars=200)  # Random text for qualifications
    #     # room_number = fake.random_int(min=1, max=100)
    #     # doctorsAssistantsRoles = random.choice([
    #     #     'Medical Assistant',
    #     #     'Nurse Practitioner',
    #     #     'Physician Assistant',
    #     #     'Clinical Nurse Specialist',
    #     #     'Surgical Assistant',
    #     #     'Radiology Technician',
    #     #     'Laboratory Technician',
    #     #     'Phlebotomist',
    #     #     'Patient Care Technician',
    #     #     'Physical Therapy Assistant',
    #     #     'Occupational Therapy Assistant',
    #     #     'Dental Assistant',
    #     #     'Optometric Assistant',
    #     #     'Chiropractic Assistant',
    #     #     'Orthopedic Assistant',
    #     #     'Pediatric Assistant',
    #     #     'Geriatric Care Assistant',
    #     #     'Anesthesia Technician',
    #     #     'Cardiology Technician',
    #     #     'Emergency Medical Technician (EMT)'
    #     # ])
    #     service_names = random.choice([
    #         "Ultrasound",
    #         "Tooth Extraction",
    #         "Dental Cleaning",
    #         "Root Canal Treatment",
    #         "Allergy Testing",
    #         "Cardiology Consultation",
    #         "Vaccination",
    #         "Physical Therapy",
    #         "Skin Biopsy",
    #         "Prenatal Checkup",
    #         "Chiropractic Adjustment",
    #         "Orthopedic Surgery",
    #         "Eye Exam",
    #         "Hearing Test",
    #         "Flu Shot",
    #         "CT Scan",
    #         "Blood Test",
    #         "MRI Scan",
    #         "X-Ray",
    #         "Dietary Consultation"
    #     ])
    #     doctor_service_duration = random.choice([15, 20, 30, 45, 60])
    #     doctor_service_cost = random.choice([25, 35, 75, 100, 49, 200])
    # services_ids = random.choice([1, 2, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    # appointment_time = random.choice(
    #         ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
    #          '15:00'])

    #     today = datetime.datetime.now().date()
    #
    #     # Calculate the start and end dates for the next week
    #     #  starts 7 days from today, and ends 14 days from today
    #     start_of_next_week = today + datetime.timedelta(days=(7 - today.weekday()))
    #     end_of_next_week = start_of_next_week + datetime.timedelta(days=6)
    #
    #     # Generate a random date between the start and end of next week
    #     random_date = fake.date_between(start_date=start_of_next_week, end_date=end_of_next_week)
    #
    #     # Format the date in the desired format
    #     formatted_date = random_date.strftime("%a %b %d %Y")
    # patient_id = random.choice(
    #     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    #      31, 32, 33, 34, 35, 36, 37, 38, 39, 40])
    #
    # start_date = datetime(2024, 7, 1)
    # end_date = datetime(2024, 8, 31, 23, 59, 59, 999999)
    #
    # # Generate a random date and time within the year 2024
    # random_datetime = fake.date_time_between(start_date=start_date, end_date=end_date)
    #
    # # Format the date and time in the desired format
    # formatted_datetime = random_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
    #
    # data = supabase_faker.table('appointments').insert({
    #         'patient_id': patient_id,
    #         'appointment_date': formatted_datetime,
    #         'appointment_time': appointment_time,
    #         'doctor_service_relation_id': services_ids,
    #         'appointment_type': 'follow-up',
    #         'created_at': formatted_datetime
    #
    #     }).execute()
    #
    # data = supabase_faker.table('billings').insert({
    #     "appointment_id": random_doctor_id,
    #     "patient_id": patient_id,
    #     "total_amount": 100,
    #     "coverage_percentage": 3,
    #     "net_amount": 97,
    #     "status": 'paid',
    #     "payment_method": random.choice(["Cash", "Card"]),
    #     "billing_date": formatted_datetime
    #
    # }).execute()
#
#     # data = supabase_faker.table('doctors_services_relation').insert({
#     #     'doctor_id': random_doctor_id,
#     #     'service_name': service_names,
#     #     'doctor_service_cost': doctor_service_cost,
#     #     'doctor_service_duration': doctor_service_duration,
#     #     'doctor_service_status': 'Active',
#     # }).execute()
#     #
#     # doctor_service_relation_id = data.data[0]['doctor_service_relation_id']
#     # print(doctor_service_relation_id)
#     #
#     # for i in range(3):
#     #     random_day = random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
#     #     time_slots = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00',
#     #                   '14:30', '15:00']
#     #     time_increment = random.choice([15, 30, 45, 60])
#     #     time_increment_unit = "Minutes"
#     #     start_time = '09:00'
#     #     end_time = '15:00'
#     #     random_assistants_id = random.choice(
#     #         [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
#     #
#     #     supabase_faker.table('doctors_schedules').insert({
#     #         "day": random_day,
#     #         "time_slots": ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
#     #                        '14:00', '14:30', '15:00'],
#     #         'time_increment': time_increment, 'time_increment_unit': 'Minutes',
#     #         "start_time": start_time, 'end_time': end_time,
#     #         "doctor_id": random_assistants_id,
#     #         "doctor_service_relation_id": doctor_service_relation_id,
#     #     }).execute()
#     #
#     #     supabase_faker.table('doctor_service_assistants_relation').insert({
#     #         "assistant_id": random_doctor_id,
#     #         "doctor_service_relation_id": doctor_service_relation_id,
#     #     }).execute()
#
#     # data = supabase_faker.auth.sign_up({
#     #     "email": patient_email,
#     #     "password": "hell332233",
#     #     "options": {
#     #         "data": {
#     #             "first_name": first_name,
#     #             "last_name": last_name,
#     #             "username": '',
#     #             "user_role": user_role,
#     #             "image_id": 1
#     #         }
#     #     }
#     # })
#
#     # data = supabase_faker.table('referring_doctors').insert({
#     #     "first_name": first_name,
#     #     "last_name": last_name,
#     #     "category": reportFields,
#     #     "specialty": specialty,
#     #     "email": patient_email,
#     #     "phone_number": patient_phone_number,
#     #     "address": patient_address,
#     #
#     # }).execute()
#
#     # data = supabase_faker.table('categories').insert({
#     #     "name": reportFields,
#     #
#     # }).execute()
