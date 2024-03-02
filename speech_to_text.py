import speech_recognition as sr
import spacy
import re
import phonenumbers
from database_operations import (
    save_appointment,
    update_appointment,
    cancel_appointment,
    check_existing_appointment,
)

# Load English language model for spaCy
nlp = spacy.load("en_core_web_md")


class DoctorAssistant:
    def __init__(self):
        self.booking_in_progress = False
        self.expecting_time_for_booking = False
        self.expecting_credentials = False
        self.current_action = ""
        self.current_name = None
        self.current_phone_number = None
        self.current_appointment_time = None

    def listen_on_button_click(self):
        with self.microphone as source:
            print("Listening...")
            audio = self.recognizer.listen(source)

        try:
            user_input = self.recognizer.recognize_google(audio)
            print("User:", user_input)
            return user_input
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that. Can you please repeat?"
        except sr.RequestError as e:
            return f"Error occurred while processing audio; {e}"

    def process_command(self, command):
        if self.expecting_time_for_booking:
            return self.book_appointment(command)
        elif self.expecting_credentials:
            return self.process_credentials(command)
        elif self.is_booking_appointment(command):
            if not self.booking_in_progress:
                self.booking_in_progress = True
                self.expecting_time_for_booking = True
                self.current_action = "booking"
                return "When would you like to book the appointment?"
            else:
                return self.book_appointment(command)
        elif self.is_reschedule_appointment(command):
            return self.reschedule_appointment(command)
        elif self.is_cancel_appointment(command):
            return self.cancel_appointment(command)
        elif self.is_check_availability(command):
            return self.get_available_slots(command)
        else:
            return "I'm sorry, I didn't understand. Can you please repeat?"

    def is_booking_appointment(self, command):
        doc = nlp(command)
        booking_queries = [
            "book appointment",
            "schedule appointment",
            "make appointment",
            "create appointment",
        ]
        for query in booking_queries:
            if doc.similarity(nlp(query)) > 0.3:
                return True
        return False

    def is_reschedule_appointment(self, command):
        doc = nlp(command)
        reschedule_queries = [
            "reschedule appointment",
            "change appointment",
            "move appointment",
        ]
        for query in reschedule_queries:
            if doc.similarity(nlp(query)) > 0.5:
                return True
        return False

    def is_cancel_appointment(self, command):
        doc = nlp(command)
        cancel_queries = ["cancel appointment", "delete appointment"]
        for query in cancel_queries:
            if doc.similarity(nlp(query)) > 0.5:
                return True
        return False

    def is_check_availability(self, command):
        doc = nlp(command)
        availability_queries = [
            "available slots",
            "available appointments",
            "appointment availability",
        ]
        for query in availability_queries:
            if doc.similarity(nlp(query)) > 0.5:
                return True
        return False

    def book_appointment(self, command):
        appointment_time = self.extract_time(command)
        if appointment_time:
            if self.current_action == "booking":
                self.expecting_credentials = True
                self.expecting_time_for_booking = False
                return (
                    "Please provide your name and phone number to complete the booking."
                )
            else:
                update_appointment(
                    self.current_name, self.current_phone_number, appointment_time
                )
                self.booking_in_progress = False
                self.expecting_time_for_booking = False
                return f"Your appointment has been updated to {appointment_time}."
        else:
            return "I'm sorry, I couldn't extract the appointment time. Can you please provide the time?"

    def reschedule_appointment(self, command):
        appointment_time = self.extract_time(command)
        if appointment_time:
            self.current_appointment_time = appointment_time
            # Check if the user has an existing appointment
            existing_appointment = check_existing_appointment(
                self.current_name, self.current_phone_number
            )
            if existing_appointment:
                update_appointment(
                    self.current_name, self.current_phone_number, appointment_time
                )
                self.booking_in_progress = False
                self.expecting_time_for_booking = False
                return f"Your appointment has been rescheduled to {appointment_time}."
            else:
                # No existing appointment found, proceed to book a new one
                self.current_action = "booking"
                self.expecting_credentials = True
                self.expecting_time_for_booking = False
                return (
                    "It seems you don't have an existing appointment. "
                    "Please provide your name and phone number to book a new appointment."
                )
        else:
            self.expecting_time_for_booking = True
            return "I'm sorry, I couldn't extract the new appointment time. Can you please provide the time?"

    def cancel_appointment(self, command):
        appointment_time = self.extract_time(command)
        if appointment_time:
            if self.current_action == "canceling":
                cancel_appointment(self.current_name, self.current_phone_number)
                self.booking_in_progress = False
                self.expecting_time_for_booking = False
                return f"Your appointment scheduled for {appointment_time} has been canceled."
            else:
                self.expecting_credentials = True
                self.expecting_time_for_booking = False
                return "Please provide your name and phone number to proceed with cancellation."
        else:
            self.expecting_time_for_booking = True
            return "I'm sorry, I couldn't extract the appointment time to cancel. Can you please provide the time?"

    def get_available_slots(self, command):
        # Placeholder logic to retrieve available appointment slots
        available_slots = ["10 am", "2 pm", "4 pm"]
        return ", ".join(available_slots)

    def extract_time(self, command):
        # Extract datetime information using spaCy
        doc = nlp(command)
        for token in doc:
            if token.ent_type_ == "TIME":
                self.current_appointment_time = token.text
                return token.text
        return None

    def process_credentials(self, command):
        # Define a regex pattern to match phone number-like sequences
        phone_pattern = r"\d+\s?\d+\s?\d+"

        # Placeholder logic to process credentials and complete the booking, rescheduling, or cancellation
        name = None
        phone_number = None

        # Search for name and phone number using spaCy and regex
        doc = nlp(command)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip()
                self.current_name = name

        phone_match = re.search(phone_pattern, command.lower())

        if phone_match:
            phone_number = phone_match.group().strip()
            self.current_phone_number = phone_number

        # If both name and phone number are provided, proceed with the action
        if name and phone_number:
            if self.current_action == "booking":
                # Save appointment
                save_appointment(
                    self.current_name,
                    self.current_phone_number,
                    self.current_appointment_time,
                )
                self.expecting_credentials = False
                return f"Thank you, {name}. Your appointment has been booked for {self.current_appointment_time}."
            elif self.current_action == "rescheduling":
                # Update appointment
                update_appointment(name, phone_number, self.current_appointment_time)
                self.expecting_credentials = False
                return f"Thank you, {name}. Your appointment has been rescheduled to {self.current_appointment_time}."
            else:
                return "I'm sorry, I couldn't understand the context. Please provide your name and phone number again."
        # If only name is provided, store it and ask for phone number
        elif name:
            # Check if phone number is already provided
            if self.current_phone_number:
                # Phone number is already provided, proceed with the action
                return self.process_credentials(f"{name} {self.current_phone_number}")
            else:
                self.current_name = name
                return "Please provide your phone number."
        # If only phone number is provided, store it and ask for name
        elif phone_number:
            # Check if name is already provided
            if self.current_name:
                # Name is already provided, proceed with the action
                return self.process_credentials(f"{self.current_name} {phone_number}")
            else:
                self.current_phone_number = phone_number
                return "Please provide your name."
        # If neither name nor phone number is provided, prompt again for both
        else:
            return "I'm sorry, I couldn't extract your name or phone number. Please provide your name and phone number."
