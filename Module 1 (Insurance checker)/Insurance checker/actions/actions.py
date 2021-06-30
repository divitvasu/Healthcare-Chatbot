# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher

from rasa_sdk.types import DomainDict

import sqlite3
from sqlite3 import Error

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_read_query(conn, query):
    cur = conn.cursor()
    result = None
    try:
        cur.execute(query)
        result = cur.fetchall()
        return result
    except Error as e:
        print(f"the error '{e}' occured")

def execute_update(conn,query):
    cur = conn.cursor()
    try:
        cur.execute(query)
        conn.commit()
    except Error as e:
        print(f"the error '{e}' occured")
        
def remove_bad_chars_int(chars):
    bad_chars = [',', ')', '(',]
    newlist = []
    for c in chars:
        c = str(c)
        c = ''.join(i for i in c if not i in bad_chars)
        newlist.append(c)
    return newlist

def remove_bad_chars(chars):
    bad_chars = [',', ')', '(',]
    newlist = []
    for c in chars:
        c = ''.join(i for i in c if not i in bad_chars)
        newlist.append(c)
    return newlist


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello! Please select one of the following"
                                 +"\n View member information - view"
                                 +"\n Check Claim Status - claim"
                                 +"\n Update Information - update")

        return []


class ValidateInputDetailsForm(FormValidationAction):
    
    def name(self) -> Text:
        return "validate_input_details_form"
            
    
    def validate_member_id(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                           ) -> Dict[Text, Any]:
        print("\nvalidating member id\n")
        conn = create_connection("C:\\Users\\divit\\Downloads\\sqlitestudio-3.3.3\\SQLiteStudio\\Database\\HealthInsurance")
        
        query1 = "select ID from Member_details;"
        
        id_data = execute_read_query(conn,query1)
        
        member_id_list = remove_bad_chars_int(id_data)
        
        if slot_value in member_id_list:
            {"isMember":True}
            return {"member_id":slot_value}
        else:
            dispatcher.utter_message("Please re-check your member ID. I'm assuming you missed a number.")
            return {"member_id":None}

    
    def validate_member_name(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                           ) -> Dict[Text, Any]:
        print("validating member name\n")
        mem_id = tracker.get_slot("member_id")
        query2 = f"SELECT name from Member_details where ID = {mem_id};"
        query3 = f"SELECT address_line1 from Member_details where ID = {mem_id};"
        query4 = f"SELECT zipcode from Member_details where ID = {mem_id};"
        query5 = f"SELECT phone from Member_details where ID = {mem_id};"
        
        conn = create_connection("C:\\Users\\divit\\Downloads\\sqlitestudio-3.3.3\\SQLiteStudio\\Database\\HealthInsurance")
        
        name_data = execute_read_query(conn,query2)
        print(name_data)
        
        member_name_list = remove_bad_chars(name_data)
        print(member_name_list)
        
        if slot_value in member_name_list:
            address = remove_bad_chars(execute_read_query(conn,query3))[0]
            print("address = ",address)
            zipcode = remove_bad_chars_int(execute_read_query(conn,query4))[0]
            print("zipcode = ",zipcode)
            phone = remove_bad_chars_int(execute_read_query(conn,query5))[0]
            print("phone =",phone)
            return {"member_name":slot_value,"address":address,"zip_code":zipcode,"phone":phone}
        else:
            dispatcher.utter_message("Please re-check the spelling. I'm assuming you mis-spelled.")
            return {"member_name":None}            


class ValidateClaimForm(FormValidationAction):
    
    def name(self) -> Text:
        return "validate_claim_form"
            
    def validate_member_id(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                           ) -> Dict[Text, Any]:
        print("\nvalidating member id in claims\n")
        conn = create_connection("C:\\Users\\divit\\Downloads\\sqlitestudio-3.3.3\\SQLiteStudio\\Database\\HealthInsurance")
        
        query1 = "select ID from Member_details;"
        
        id_data = execute_read_query(conn,query1)
        
        member_id_list = remove_bad_chars_int(id_data)
        
        if slot_value in member_id_list:
            return {"member_id":slot_value}
        else:
            dispatcher.utter_message("Please re-check your member ID. I'm assuming you missed a number.")
            return {"member_id":None}

    
    def validate_claims(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                           ) -> Dict[Text, Any]:
        print("validating claims\n")
        has_claims = False
        conn = create_connection("C:\\Users\\divit\\Downloads\\sqlitestudio-3.3.3\\SQLiteStudio\\Database\\HealthInsurance")
        mem_id = tracker.get_slot("member_id")
        print(mem_id)
        query2 = f"SELECT c.claim_id from claim_x_member c join Member_details m on m.ID=c.member_id where m.ID = {mem_id};"
        claims_data = remove_bad_chars_int(execute_read_query(conn,query2))
        
        if len(claims_data) > 0:
            has_claims = True
        
        slot_value = str(slot_value)
        print(slot_value)
        if has_claims:
            if slot_value in claims_data:
                query3 = f"SELECT status from Claims where claim_number = {slot_value};"
                claim_status = remove_bad_chars(execute_read_query(conn,query3))[0]
                dispatcher.utter_message(f"Status for Claim {slot_value} is {claim_status}")
                return {"user_has_claims":True,"claims":claims_data,"claim_status":claim_status}
            else:
                dispatcher.utter_message("Incorrect claim value. Please re-check.")
                return {"claim_status":None}
        else:
            dispatcher.utter_message("You don't seem to have any claims at the moment."
                                     +"\nPlease contact customer care for more information.")
            return {"user_has_claims":False,"claims":None,"claim_status":None}

class ValidateNameForm(FormValidationAction):
    
    def name(self) -> Text:
        return "validate_name_form"
            
    def validate_member_id(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                           ) -> Dict[Text, Any]:
        print("\nvalidating member id in names\n")
        conn = create_connection("C:\\Users\\divit\\Downloads\\sqlitestudio-3.3.3\\SQLiteStudio\\Database\\HealthInsurance")
        
        query1 = "select ID from Member_details;"
        
        id_data = execute_read_query(conn,query1)
        
        member_id_list = remove_bad_chars_int(id_data)
        
        if slot_value in member_id_list:
            return {"member_id":slot_value}
        else:
            dispatcher.utter_message("Please re-check your member ID. I'm assuming you missed a number.")
            return {"member_id":None}        
       
    def validate_new_member_name(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                           ) -> Dict[Text, Any]:
        print("validating member name in name form\n")
        mem_id = tracker.get_slot("member_id")
        
        query2 = f"SELECT EXISTS(SELECT ID FROM Member_details WHERE ID = {mem_id});"
        
        conn = create_connection("C:\\Users\\divit\\Downloads\\sqlitestudio-3.3.3\\SQLiteStudio\\Database\\HealthInsurance")
        
        user_exists = remove_bad_chars_int(execute_read_query(conn,query2))[0]
        
        if user_exists == '1':
            query3 = f"UPDATE Member_details SET name = '{slot_value}' where ID = {mem_id};"
            query4 = f"SELECT address_line1 from Member_details where ID = {mem_id};"
            query5 = f"SELECT zipcode from Member_details where ID = {mem_id};"
            query6 = f"SELECT phone from Member_details where ID = {mem_id};"
            execute_update(conn,query3)
            address = remove_bad_chars(execute_read_query(conn,query4))[0]
            print("address = ",address)
            zipcode = remove_bad_chars_int(execute_read_query(conn,query5))[0]
            print("zipcode = ",zipcode)
            phone = remove_bad_chars_int(execute_read_query(conn,query6))[0]
            print("phone =",phone)
            return {"new_member_name":slot_value,"address":address,"zip_code":zipcode,"phone":phone}
        else:
            dispatcher.utter_message("An internal error has occurred. Please contact customer care.")
            return {"new_member_name":None}


class ValidateAddressForm(FormValidationAction):
    
    def name(self) -> Text:
        return "validate_address_form"
            
    def validate_member_id(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                           ) -> Dict[Text, Any]:
        print("\nvalidating member id in names\n")
        conn = create_connection("C:\\Users\\divit\\Downloads\\sqlitestudio-3.3.3\\SQLiteStudio\\Database\\HealthInsurance")
        
        query1 = "select ID from Member_details;"
        
        id_data = execute_read_query(conn,query1)
        
        member_id_list = remove_bad_chars_int(id_data)
        
        if slot_value in member_id_list:
            return {"member_id":slot_value}
        else:
            dispatcher.utter_message("Please re-check your member ID. I'm assuming you missed a number.")
            return {"member_id":None}        
       
    def validate_new_address(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                           ) -> Dict[Text, Any]:
        print("validating member name in name form\n")
        mem_id = tracker.get_slot("member_id")
        
        query2 = f"SELECT EXISTS(SELECT ID FROM Member_details WHERE ID = {mem_id});"
        
        conn = create_connection("C:\\Users\\divit\\Downloads\\sqlitestudio-3.3.3\\SQLiteStudio\\Database\\HealthInsurance")
        
        user_exists = remove_bad_chars_int(execute_read_query(conn,query2))[0]
        
        if user_exists == '1':
            query3 = f"UPDATE Member_details SET address_line1 = '{slot_value}' where ID = {mem_id};"
            query4 = f"SELECT name from Member_details where ID = {mem_id};"
            query5 = f"SELECT zipcode from Member_details where ID = {mem_id};"
            query6 = f"SELECT phone from Member_details where ID = {mem_id};"
            execute_update(conn,query3)
            name = remove_bad_chars(execute_read_query(conn,query4))[0]
            print("name = ",name)
            zipcode = remove_bad_chars_int(execute_read_query(conn,query5))[0]
            print("zipcode = ",zipcode)
            phone = remove_bad_chars_int(execute_read_query(conn,query6))[0]
            print("phone =",phone)
            return {"member_name":name,"new_address":slot_value,"zip_code":zipcode,"phone":phone}
        else:
            dispatcher.utter_message("An internal error has occurred. Please contact customer care.")
            return {"new_address":None}

class ValidatePhoneForm(FormValidationAction):
    
    def name(self) -> Text:
        return "validate_phone_form"
            
    def validate_member_id(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                           ) -> Dict[Text, Any]:
        print("\nvalidating member id in names\n")
        conn = create_connection("C:\\Users\\divit\\Downloads\\sqlitestudio-3.3.3\\SQLiteStudio\\Database\\HealthInsurance")
        
        query1 = "select ID from Member_details;"
        
        id_data = execute_read_query(conn,query1)
        
        member_id_list = remove_bad_chars_int(id_data)
        
        if slot_value in member_id_list:
            return {"member_id":slot_value}
        else:
            dispatcher.utter_message("Please re-check your member ID. I'm assuming you missed a number.")
            return {"member_id":None}        
       
    def validate_new_phone(self,
                           slot_value: Any,
                           dispatcher: CollectingDispatcher,
                           tracker: Tracker,
                           domain: DomainDict,
                           ) -> Dict[Text, Any]:
        print("validating member name in name form\n")
        mem_id = tracker.get_slot("member_id")
        
        query2 = f"SELECT EXISTS(SELECT ID FROM Member_details WHERE ID = {mem_id});"
        
        conn = create_connection("C:\\Users\\divit\\Downloads\\sqlitestudio-3.3.3\\SQLiteStudio\\Database\\HealthInsurance")
        
        user_exists = remove_bad_chars_int(execute_read_query(conn,query2))[0]
        
        if user_exists == '1':
            if slot_value.isdigit() and len(slot_value) == 10:
                query3 = f"UPDATE Member_details SET phone = {slot_value} where ID = {mem_id};"
                query4 = f"SELECT name from Member_details where ID = {mem_id};"
                query5 = f"SELECT zipcode from Member_details where ID = {mem_id};"
                query6 = f"SELECT address_line1 from Member_details where ID = {mem_id};"
                execute_update(conn,query3)
                name = remove_bad_chars(execute_read_query(conn,query4))[0]
                print("name = ",name)
                zipcode = remove_bad_chars_int(execute_read_query(conn,query5))[0]
                print("zipcode = ",zipcode)
                address = remove_bad_chars(execute_read_query(conn,query6))[0]
                print("address =",address)
                return {"member_name":name,"address":address,"zip_code":zipcode,"new_phone":slot_value}
            else:
                dispatcher.utter_message("Please enter a valid phone number.")
                return {"new_phone":None}
        else:
            dispatcher.utter_message("An internal error has occurred. Please contact customer care.")
            return {"new_phone":None}
        