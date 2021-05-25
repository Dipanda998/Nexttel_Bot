# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from typing import Any, Text, Dict, List, Union
#
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
import re
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from rasa.core.channels.channel import InputChannel


#
#

# class ActionCheckNumber(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_user_details_form"
    
#     @staticmethod
#     def validate_number_code(self,
#                              value: Any,
#                              dispatcher: CollectingDispatcher,
#                              tracker: Tracker,
#                              domain: DomainDict)-> Dict[Text, Any]:
        
#         if re.match(r"^6{2}", value) != None and len(value)==9 and value.isdigit()==True:
#             return {"number_code": value}
#         else:
#             dispatcher.utter_message(template="utter_erreur_numero")
#             return {"number_code":None} 
    
    
# class UserForm(FormAction):
    
#     def name(self)->Text:
#         return "user_details_form"
    
# #     @staticmethod
# #     def required_slots(tracker: Tracker)-> List[Text]:
# #         """A list of required slots that the form has to fill"""
# #         return ["number_code"]
    
#     def submit(self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],) -> List[Dict]:
        
#         dispatcher.utter_message(template="utter_submit")
#         return []
   

        
#         number_code = tracker.get_slot("number_code")

# class MyIO(InputChannel):
#     def name() -> Text:
#         """Name of your custom channel."""
#         return "King_francais"

class SendMail(Action):
    def name(self) -> Text:
        return "action_send_mail"

    def run (
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[EventType]:
        numero = tracker.get_slot("number"),
        nom = tracker.get_slot("name"),
        probleme = tracker.get_slot("probleme")
        fromaddr = "teskingpro2@gmail.com"
        password = "Kingpro3.p0"
        toaddr = "testfrancoisking@gmail.com"
        subject = "Problème"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject
        body = "M ou Mme << {} >> qui a pour numero le << {} >> rencontre un problème.\nLe Son problème est le suivant:\n{}".format(nom, numero, probleme)
        
        msg.attach(MIMEText(body,'plain'))
        
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        
        try:
            s.login(fromaddr, password)
            text = msg.as_string()
            s.sendmail(fromaddr, toaddr, text)
            print("Envoie reussi")
            dispatcher.utter_message(template="utter_transfert_effectue")
        except:
            dispatcher.utter_message(template="utter_erreur_transfert")
            print("Une erreur est survenue lors de l'envoi de la requête")
        finally:
            s.quit()
        return []
    
#     def sendEmail(numero, nom, probleme,dispatcher: CollectingDispatcher):
#         fromaddr = "teskingpro2@gmail.com"
#         password = "Kingpro3.p0"
#         toaddr = "testfrancoisking@gmail.com"
#         subject = "Problème"
#         msg = MIMEMultipart()
#         msg['From'] = fromaddr
#         msg['To'] = toaddr
#         msg['Subject'] = subject
#         body = "M ou Mme << {} >> qui a pour numero le << {} >> rencontre un problème.\nLe Son problème est le suivant:\n{}".format(nom, numero, probleme)
        
#         msg.attach(MIMEText(body,'plain'))
        
#         s = smtplib.SMTP('smtp.gmail.com', 587)
#         s.starttls()
        
#         try:
#             s.login(fromaddr, password)
#             text = msg.as_string()
#             s.sendmail(fromaddr, toaddr, text)
#             print("Envoie reussi")
#             dispatcher.utter_message(text="Transfert effectué")
#         except:
#             dispatcher.utter_message(text="Une erreur est survenue lors du transfert de votre requête. Veuillez vérifier l'état de votre connexion Internet")
#             print("Une erreur est survenue lors de l'envoi de la requête")
#         finally:
#             s.quit()
    

    
    


class ValidateRestaurantForm(Action):
    def name(self) -> Text:
        return "user_details_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["name", "number", "probleme"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]
       
class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_details_thanks")
        
class ResetAllSlots(Action):
    def name(self) -> Text:
        return "action_reset_slots"
    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]
        
# class ActionHandoff(Action):
#     def name(self) -> Text:
#         return "action_handoff"

#     async def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[EventType]:

#         dispatcher.utter_message(template="utter_handoff")
#         handoff_to = tracker.get_slot("handoff_to")

#         handoff_bot = handoff_config.get(handoff_to, {})
#         url = handoff_bot.get("url")

#         if url:
#             if tracker.get_latest_input_channel() == "rest":
#                 dispatcher.utter_message(
#                     json_message={
#                         "handoff_host": url,
#                         "title": handoff_bot.get("title"),
#                     }
#                 )
#             else:
#                 dispatcher.utter_message(
#                     template="utter_wouldve_handed_off", handoffhost=url
#                 )
#         else:
#             dispatcher.utter_message(template="utter_no_handoff")

#         return []
    
    
#     @staticmethod
#     def slot_mappings(self)-> Dict[Text, Union[Dict, List[Dict]]]:
#         return {
#             "numero_code":[
#                 self.from_entity(entity="numero", intent="numero_telephone"),
#                      ],
#         }

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
        
#         required_slots = ["numero"]
#         for slot_name in required_slots:
#             if tracker.slots.get(slot_name) is None:
#                 return[Slotset("required_slot", slot_name)]
            
#         return [Slotset("required_slot", None)] 