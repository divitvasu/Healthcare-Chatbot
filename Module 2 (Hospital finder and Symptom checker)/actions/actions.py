# This files contains your custom actions which can be used to run

# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import json
from typing import Any, Text, Dict, List
import googlemaps
import requests
from googlesearch import search
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher


modification = 0
choice_array = []


class ActionHospitalLocation(Action):

    def name(self) -> Text:
        return "action_hospital_location"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        poi_provided = str(tracker.get_slot("place_of_interest"))
        location_provided = str(tracker.get_slot("location"))
        print(location_provided)
        Address_found_from_API = ActionHospitalLocation.locate(poi_provided, location_provided)
        for i in Address_found_from_API:
            dispatcher.utter_message(i)
        print(Address_found_from_API)

        return [SlotSet("address", Address_found_from_API)]

    # dispatcher.utter_message(template="Here are the hospitals near {}!".format(location_provided))
    # return []

    def locate(place_of_interest, location):

        API_Key = 'AIzaSyBMLuC0-xkj6PV5BdUxvgh5IhbadAd9GkA'
        gmaps = googlemaps.Client(key=API_Key)
        long_lati = gmaps.geocode(str(location))
        res_long_lati = long_lati[0]
        lat = str(res_long_lati["geometry"]['location']["lat"])
        Long = str(res_long_lati["geometry"]['location']["lng"])

        response_result = gmaps.places_nearby(location=(str(lat), str(Long)), keyword=str(place_of_interest),
                                              rank_by="distance", open_now=False, type="doctor")

        i = 1
        messages = []
        for place in response_result['results']:
            placeID = place['place_id']
            requirements = ['formatted_address', "formatted_phone_number", 'url']
            place_details = gmaps.place(place_id=placeID, fields=requirements)
            info = place_details['result']
            messages.append(str(i) + ". Location Name : " + place['name'] + "\nAddress : " + place_details['result'][
                'formatted_address'] + "\nPh. no :" + place_details['result'][
                                'formatted_phone_number'] + "\nGoogle Map Link : " + place_details['result']['url'])

            i += 1
            if i == 6:
                break

        return messages


class InitialQuery(Action):

    def name(self) -> Text:
        return "action_initial_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        gender_provided = str(tracker.get_slot("gender"))
        age_provided = str(tracker.get_slot("age"))
        symptom_initial_provided = str(tracker.get_slot("symptom_initial"))
        SymptomIDs = InitialQuery.firstSymptomCollector(gender_provided, age_provided, symptom_initial_provided)

        # Run close:
        return [SlotSet("ids", SymptomIDs)]

    def firstSymptomCollector(gender_provided, age_provided, symptom_initial_provided):

        url = "https://api.infermedica.com/v3/parse"
        App_ID = 'e8ec3a23'
        App_Key = 'bb5f99fdf290881089f3c151097de513'
        age = int(age_provided)
        gender = (str(gender_provided.lower()))
        symptom_query = str(symptom_initial_provided)

        payload = json.dumps({
            "text": symptom_query,
            "age": {
                "value": age
            },
            "sex": gender
        })
        headers = {
            'App-Id': App_ID,
            'App-Key': App_Key,
            'Authorization': 'Basic ZThlYzNhMjM6IGJiNWY5OWZkZjI5MDg4MTA4OWYzYzE1MTA5N2RlNTEzCSA=',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # Converting the response received to the JSON Format
        info = response.json()

        # Staring of the List:
        possibleSymptomsIDs = {}
        for symid in info["mentions"]:
            # Considering one of the symptoms as Initial
            if "Initial" not in possibleSymptomsIDs:
                possibleSymptomsIDs["Initial"] = symid["id"]
            possibleSymptomsIDs[symid["id"]] = symid["choice_id"]

        return possibleSymptomsIDs


class DiagnosisQuery(Action):

    def name(self) -> Text:
        return "action_diagnosis_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        gender_provided = str(tracker.get_slot("gender"))
        age_provided = str(tracker.get_slot("age"))
        SymptomsIDs = (tracker.get_slot("ids"))
        Question, Ques_Ans, IDs = DiagnosisQuery.diagnosis(gender_provided, age_provided, SymptomsIDs)

        dispatcher.utter_message(Question)
        # Run close:
        return [SlotSet("prompts", Ques_Ans), SlotSet("idkey", IDs)]

    def diagnosis(gender_provided, age_provided, possibleSymptomsIDs):
        url = "https://api.infermedica.com/v3/diagnosis"
        App_ID = 'e8ec3a23'
        App_Key = 'bb5f99fdf290881089f3c151097de513'
        age = int(age_provided)
        gender = (str(gender_provided.lower()))

        evidenceList = []
        # Getting the varibale Initial
        Initial_True = possibleSymptomsIDs["Initial"]

        for id, choiceID in possibleSymptomsIDs.items():
            if id == "Initial":
                continue
            elif id == Initial_True:  # Only for considering Initial as Initial.
                evidenceList.append({"id": id, "choice_id": choiceID, "source": "initial"})
            else:
                evidenceList.append({"id": id, "choice_id": choiceID})

        print(evidenceList)
        payload = json.dumps({
            "sex": gender,
            "age": {
                "value": age
            },
            "evidence": evidenceList
        })
        headers = {
            'App-Id': App_ID,
            'App-Key': App_Key,
            'Authorization': 'Basic ZThlYzNhMjM6IGJiNWY5OWZkZjI5MDg4MTA4OWYzYzE1MTA5N2RlNTEzCSA=',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        r = response.json()
        #  print(r['question']['items'])

        questions_to_ask = []
        IDs = []
        for i in (r['question']['items']):
            response_str = ""
            response_str += str(i['name']) + "\n"
            # Storing the ID
            IDs.append(i['id'])
            # print(ID)
            # print(i['name'])
            order = 1
            for j in (i['choices']):
                response_str += str(order) + ". " + str(j['label']) + "\n"
                order += 1
            questions_to_ask.append(response_str)

        return (r["question"]["text"], questions_to_ask, IDs)


class ResponseQuery(Action):
    global modification
    
    def name(self) -> Text:
        return "action_response_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global modification
        gender_provided = str(tracker.get_slot("gender"))
        age_provided = str(tracker.get_slot("age"))
        Choice = str(tracker.get_slot("choice"))
        Ques_Ans = (tracker.get_slot("prompts"))

        if Choice != 'a' and Choice != 'A' and Choice != 'a.' and Choice != "A." and Choice != "null":
            count = 0
            for q in Ques_Ans:
                if count != modification:
                    count += 1
                    continue
                dispatcher.utter_message(q)
                modification += 1
                return [FollowupAction('action_listen')]  # CHECK!!
        else:
            modification = 0
            return [SlotSet("choice", "null")]
		# elif mod = 0 and count =5:                                        # check on this!!!
			# return [SlotSet("choice", "null"),SlotSet("breaker", true)]

class StorageQuery(Action):
    global choice_array

    def name(self) -> Text:
        return "action_storage_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global choice_array
        Choice = str(tracker.get_slot("choice"))
        choice_array.append(Choice)
        IDs = (tracker.get_slot("idkey"))
        SymptomsIDs = (tracker.get_slot("ids"))

        if len(choice_array) >= len(IDs):
            for i in range(len(IDs)):
                if 'a' == choice_array[i] or 'A' == choice_array[i] or 'a.' == choice_array[i] or 'A.' == choice_array[i]:
                    SymptomsIDs[IDs[i]] = "present"
                elif 'b' == choice_array[i] or 'B' == choice_array[i] or 'b.' == choice_array[i] or 'B.' == \
                        choice_array[i]:
                    SymptomsIDs[IDs[i]] = "absent"
                elif 'c' == choice_array[i] or 'C' == choice_array[i] or 'c.' == choice_array[i] or 'C.' == \
                        choice_array[i]:
                    SymptomsIDs[IDs[i]] = "unknown"
            choice_array=[]
            return [SlotSet("ids", SymptomsIDs), SlotSet("flag", True)]


class FinalQuery(Action):

    def name(self) -> Text:
        return "action_final_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        gender_provided = str(tracker.get_slot("gender"))
        age_provided = str(tracker.get_slot("age"))
        SymptomsIDs = (tracker.get_slot("ids"))
        disease, output = FinalQuery.result(gender_provided, age_provided, SymptomsIDs)
        dispatcher.utter_message(disease)
        dispatcher.utter_message(output)

    def result(gender_provided, age_provided, possibleSymptomsIDs):

        url = "https://api.infermedica.com/v3/diagnosis"
        App_ID = 'e8ec3a23'
        App_Key = 'bb5f99fdf290881089f3c151097de513'
        age = int(age_provided)
        gender = (str(gender_provided.lower()))

        evidenceList = []
        # Getting the varibale Initial
        Initial_True = possibleSymptomsIDs["Initial"]

        for id, choiceID in possibleSymptomsIDs.items():

            if id == "Initial":
                continue
            elif id == Initial_True:
                evidenceList.append({"id": id, "choice_id": choiceID, "source": "initial"})
            else:
                evidenceList.append({"id": id, "choice_id": choiceID})

        payload = json.dumps({
            "sex": gender,
            "age": {
                "value": age
            },
            "evidence": evidenceList
        })
        headers = {
            'App-Id': App_ID,
            'App-Key': App_Key,
            'Authorization': 'Basic ZThlYzNhMjM6IGJiNWY5OWZkZjI5MDg4MTA4OWYzYzE1MTA5N2RlNTEzCSA=',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        r = response.json()
        disease = r['conditions'][0]['common_name']

        t1 = "After looking at your symptoms the most probable disease is: " + str(disease)

        query = "Remedies for " + str(disease)
        text = "Please look at the following links for remedies : \n"
        for j in search(query, tld="co.in", num=4, stop=3, pause=2):
            text += str(j) + "\n"

        return (t1, text)


class ResetSlots(Action):
    def name(self) -> Text:
        return "action_reset_slots"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict[Text, Any]]:
        return [SlotSet("choice", None), SlotSet("idkey", None), SlotSet("prompts", None), SlotSet("flag", False)]