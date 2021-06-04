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
from typing import Any, Text, Dict, List, Union, Optional, Callable, Awaitable, NoReturn
#
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
import re
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset
import requests
import socket

#Package pour l'envoi des mails
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv
import os
import asyncio
import inspect
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse

#Package pour la base données
from pymongo import MongoClient
import datetime
import pprint


import rasa.utils.endpoints


appel_fallback = 0
client = MongoClient('localhost', 27017)
db = client.rasa
#
#
#  buttons = [
#             {"payload": "/affirm", "title": "Yes"},
#             {"payload": "/deny", "title": "No"},
#         ]

# here = pathlib.Path(__file__).parent.absolute()
# handoff_config = (
#     ruamel.yaml.safe_load(open(f"{here}/handoff_config.yml", "r")) or {}
# ).get("handoff_hosts", {})
    

class ActionBackPrincipal(Action):
    """Execute the fallback action and goes back to the previous state of the dialogue"""
    def name(self) -> Text:
        return "action_back_principal"
    
    async def run(self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],) -> List[Dict]:
        
        
        global appel_fallback
        if appel_fallback <=1:
            dispatcher.utter_message(response="utter_reformulation")
            appel_fallback = appel_fallback + 1
            print(appel_fallback)
        else:
            current_state = tracker.current_state()
            probleme = current_state["latest_message"]["text"]
            dispatcher.utter_message(response="utter_transfert")
            appel_fallback = 0
            print(appel_fallback)
            return[SlotSet("probleme", probleme)]
        return None
    
        
class ActionSendProbleme(Action):
    def name(self) -> Text:
        return "action_send_probleme"

    async def run (
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[EventType]:
        appli = "King"
        numero = str(tracker.get_slot("numero"))
        numero = "237"+numero
        probleme = tracker.get_slot("probleme")
        pi = ["activation_internet_impossible"]
        pr = ["pas_reseau"]
        li = ["connexion_lente","impossible_surfer"]
        print(numero)
        for prob in pi:
            if probleme == prob:
                probleme = "pi"
        for prob in pr:
            if probleme == prob:
                probleme = "pr"
        for prob in li:
            if probleme == prob:
                probleme = "li"
                
        print(probleme)
        ### Connexion au serveur
        
        SERVER = "192.168.1.5"
        PORT = 12101
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        message_emis = ""
        message_emis =numero + ","+ probleme + "," + appli
        try:
            client.connect((SERVER, PORT))
            # client.sendall(bytes("This is from Client",'UTF-8'))
    #             out_data = input()
            client.send(message_emis.encode("utf8"))
        except:
            print("Une erreur s'est produite lors de la connexion au serveur")
            client.close()
            
        try:
            message_recu =  client.recv(1024).decode("utf8")
            dispatcher.utter_message(text=message_recu)
        except:
            print("Une erreur s'est produite lors de la lecture des données venant du serveur")
            client.close()
#         except asyncio.exceptions.TimeoutError():
#             print("Erreur!! Délais d'attente dépassé")
#             client.close()        
            
        client.close()
        

        
class ActionActivationInternetImpossible(Action):
    def name(self) -> Text:
        return "action_activation_internet_impossible"

    def run (
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[EventType]:
        dispatcher.utter_message(response="utter_activation_internet_impossible")
        probleme = tracker.get_intent_of_latest_message()
        return[SlotSet("probleme", probleme)]

class ActionPrixDevice(Action):
    def name(self) -> Text:
        return "action_prix_device"

    def run (
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[EventType]:
        global client
        global db
        bd = db.prix_device
        data = bd.find() 
        intent = tracker.get_intent_of_latest_message()
        if intent == "demande_box":
            liste = ["wifiBox"]
            image = ["image_box"]
        if intent == "demande_modem":
            liste = ["modemPoche"]
            image = ["image_modem"]
        if intent == "demande_telephone":
            liste = ["telephone"]
            image = ["image_phone"]
        if intent == "demande_cle":
            liste = ["cle"]   
            image = ["image_cle"]
        if intent == "prix_produits":
            liste = ["cle","telephone","wifiBox","modemPoche"]
            image = ["image_cle","image_phone","image_box","image_modem"]
        
        i=0
        while i < len(liste):
            prix = data.distinct(liste[i])
#             image = data.distinct(image[i])
            prix = prix[0]
#             image = image[0]
            dispatcher.utter_message(text=prix)
#             dispatcher.utter_message(image=image)
            i=i+1
        
class ActionSalutation(Action):
    def name(self) -> Text:
        return "action_salutation"

    def run (
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[EventType]:
        global client
        global db
        bd = db.salutation
        data = bd.find()
        saluer = data.distinct("saluerKing")
        saluer = saluer[0]
        dispatcher.utter_message(text=saluer)
        
    
class ActionListConfigInternet(Action):
    def name(self) -> Text:
        return "action_list_config_internet"

    def run (
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[EventType]:
        global client
        global db
        bd = db.config_internet
        data = bd.find()
       
        intent = tracker.get_intent_of_latest_message()
        if intent == "configuration_android":
            device = data.distinct("android")
            message_device = "Configuration Android: "
        if intent == "configuration_iphone":
            device = data.distinct("iphone")
            message_device = "Configuration Iphone: "
        if intent == "configuration_modem":
            device = data.distinct("modem")
            message_device = "Configuration Modem: "
        message = ""
        message = message + message_device+"{}\n\n".format(device[0])
        dispatcher.utter_message(text=message)
            


class ActionListForfait(Action):
    def name(self) -> Text:
        return "action_list_forfait"

    def run (
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[EventType]:
        global client
        global db
        collection = tracker.get_intent_of_latest_message()
        if collection == "internet_heure":
            bd = db.internet_heure
        if collection == "internet_jour":
            bd = db.internet_jour
        if collection == "internet_semaine":
            bd = db.internet_semaine
        if collection == "internet_mois":
            bd = db.internet_mois
        if collection == "internet_nuit":
            bd = db.internet_nuit
        if collection == "internet_weekend":
            bd = db.internet_weekend
            
        posts = bd.find()
        detail = posts.distinct("detail")
        code = posts.distinct("code")
        i=0
        message = ""
        for d in detail:
            message = message + "{}. Code: {}\n\n".format(detail[i],code[i])
            i=i+1
        
        envoie = "Nexttel propose les forfaits internet suivant: \n{}".format(message)
        dispatcher.utter_message(text=envoie)
        return []
        

class ActionStoreProbleme(Action):
    def name(self) -> Text:
        return "action_store_probleme"

    def run (
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[EventType]:

        intent = tracker.get_intent_of_latest_message()
        current_state = tracker.current_state()
        probleme = current_state["latest_message"]["text"]
    
        if intent == "prix_produits" or intent == "demande_box" or intent == "demande_telephone" or  intent == "demande_modem":
            return [SlotSet('probleme', probleme), SlotSet('categorie', "Prix de produits")]
        
        if intent == "forfait_internet":
            return [SlotSet('probleme', probleme), SlotSet('categorie', "Forfait Internet")]
        
        if intent == "connexion_impossible":
            return [SlotSet('probleme', probleme), SlotSet('categorie', "Connexion Impossible")]
        
        if intent == "activer_puce":
            return [SlotSet('probleme', probleme), SlotSet('categorie', "Activation SIM")]
        
        if intent == "identifier_puce":
            return [SlotSet('probleme', probleme), SlotSet('categorie', "Identification SIM")]
        
        if intent == "connaitre_numero":
            return [SlotSet('probleme', probleme), SlotSet('categorie', "Connaitre Numéro SIM")]
        
        if intent == "appel_sans_credit":
            return [SlotSet('probleme', probleme), SlotSet('categorie', "Appel sans crédit de communication")]
        
        if intent == "configuration_android" or intent == "configuration_iphone" or  intent == "configuration_modem" :
            return [SlotSet('probleme', probleme), SlotSet('categorie', "Configuration Internet")]
        
        if intent == "utiliser_phone_etranger":
            return [SlotSet('probleme', probleme), SlotSet('categorie', "Utiliser son mobile à l'étranger")]
        
                                

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
            dispatcher.utter_message(response="utter_transfert_effectue")
        except:
            dispatcher.utter_message(response="utter_erreur_transfert")
            print("Une erreur est survenue lors de l'envoi de la requête")
        finally:
            s.quit()
        return []
    

class ValidateRestaurantForm(Action):
    def name(self) -> Text:
        return "user_details_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["name", "number"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]
    
class ValidateUtilisateurtForm(Action):
    def name(self) -> Text:
        return "utilisateur_details_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["nom", "numero"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

    
class ValidateResoluForm(Action):
    def name(self) -> Text:
        return "resolu_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["resolu"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                if tracker.get_intent_of_latest_message() == "affirmation":
                    return [SlotSet("requested_slot", "True")]
                if tracker.get_intent_of_latest_message() == "negtion":
                    return [SlotSet("requested_slot", "False")]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]
    
class ValidateStatutConnexionForm(Action):
    def name(self) -> Text:
        return "statut_connexion_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["statut_connexion","forfait_internet"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
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
        dispatcher.utter_message(response="utter_details_thanks")

    
class StoreProbleme(Action):
    def name(self) -> Text:
        return "action_store_probleme"
    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:       
        current_state = tracker.current_state()
        probleme = current_state["latest_message"]["text"]
        return [SlotSet('probleme', probleme)]
        
class ResetAllSlots(Action):
    def name(self) -> Text:
        return "action_reset_slots"
    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        return [AllSlotsReset(), SlotSet("requested_slot", None)]
    
class ResetAllSlotsTwo(Action):
    def name(self) -> Text:
        return "action_reset_slots_two"
    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        return [AllSlotsReset(), SlotSet("requested_slot", None)]
        
class SauvegardeCSV(Action):
    def name(self) -> Text:
        return "action_sauvegarde_csv"
    
    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        file_txt= r"C:\Users\daniel\Desktop\nexttel\TAL\rasa_chatbot_fr\actions\testmoi.csv"

        exist = os.path.isfile(file_txt)
        #data = ["Problème",tracker.get_slot("resolu")]
        resolu = tracker.get_slot("resolu")
        slot = tracker.get_slot("probleme")
        categorie = tracker.get_slot("categorie")
        print("slot : {}".format(slot))
        header = ['Catégorie','Problèmes', 'Résolus']
        if exist == False:
            try:
                file = open(file_txt, 'w', newline ='')

                with file:
                    # identifying header  
                    writer = csv.DictWriter(file, fieldnames = header)

                    #writing data row-wise into the csv file
                    writer.writeheader()
                    writer.writerow({'Catégorie' : categorie,
                                     'Problèmes' : slot, 
                     'Résolus': resolu})
            except:
                print("Erreur lors de l'ouverture du fichier")
        else:
#             data = [tracker.get_slot("probleme"),tracker.get_slot("resolu") ]
            
            try:
                file = open(file_txt, 'a+', newline ='')
                with file:
                    writer = csv.DictWriter(file, fieldnames = header)
                    writer.writerow({'Catégorie' : categorie,
                        'Problèmes' : slot, 
                     'Résolus': resolu})
            except:
                print("Erreur")

class ActionForfaitInternetSouscrit(Action):
    def name(self) -> Text:
        return "action_forfait_internet_souscrit"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
         
        dispatcher.utter_message(response="utter_forfait_internet")
        return [SlotSet('statut_internet', tracker.get_intent_of_latest_message())]
    
class ActionDebutForm(Action):
    def name(self) -> Text:
        return "action_debut_formulaire"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
         
        dispatcher.utter_message(response="utter_debut_formulaire")
        return [SlotSet('forfait_souscrit', tracker.get_intent_of_latest_message())]

                
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