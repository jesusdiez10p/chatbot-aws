from asyncio import events
import json
from pathlib import Path
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase
from rasa_sdk.events import AllSlotsReset, SlotSet
import unidecode
# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
class ActionCheckExistence(Action):
    knowledge = Path("actions/partidos.txt").read_text().split("\n")

    def name(self) -> Text:
        return "action_check_existence"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot('partido').lower()
        valor = True
        if(tracker.latest_action_name=="action_get_summarize" or tracker.latest_action_name=="action_get_keys"):
            dispatcher.utter_message(text=f"")
        else:
            if name in self.knowledge:
                valor = True
            else:
                dispatcher.utter_message(
                    text=f"No reconozco a {name} como partido, estas seguro que está bien escrito?")
                valor = False
        return [SlotSet("find",valor)]

class ActionGetSummarize(Action):
    def name(self) -> Text:
        return "action_get_summarize"
    
    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open("actions/partidos.json", encoding="utf8") as file:
            datos = json.load(file)
        name = tracker.get_slot('partido').lower()
        for x in datos:
            if x['nombre'] == name:
                for t in x['temas']:
                    if tracker.get_slot('tema') in unidecode.unidecode(t['nombre']):
                        if (t['resumen']!=''):
                            dispatcher.utter_message(text=f"{t['resumen']}\n\n")
                        else:
                            dispatcher.utter_message(text=f"El partido {name} no tiene registrado informacion sobre este capítulo")
        dispatcher.utter_message(response="utter_add_task")
        slots = []
        slots.append(SlotSet("tema",None))
        slots.append(SlotSet("partido",None))
        return slots

class ActionGetKeys(Action):
    knowledge = InMemoryKnowledgeBase("actions/partidos.json")

    def name(self) -> Text:
        return "action_get_keys"
    
    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open("actions/partidos.json", encoding="utf8") as file:
            datos = json.load(file)
        name = tracker.get_slot('partido').lower()
        
        for x in datos:
            if x['nombre'] == name:
                for t in x['temas']:
                    if tracker.get_slot('tema') in unidecode.unidecode(t['nombre']):
                        if len(t['keywords'])>0:
                            dispatcher.utter_message(text=f"Estas son las ideas principales de {name} en su plan de gobierno: ")
                            for k in t['keywords']:
                                dispatcher.utter_message(text=f"- {k}")
                        else:
                            dispatcher.utter_message(text=f"El partido {name} no tiene registrado informacion sobre este capítulo")
        dispatcher.utter_message(response="utter_add_task")
        slots = []
        slots.append(SlotSet("tema",None))
        slots.append(SlotSet("partido",None))
        return slots

class ActionGetPartidoTopic(Action):
    
    def name(self) -> Text:
        return "action_get_partido_topic"
    
    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        with open("actions/partidos.json", encoding="utf8") as file:
            datos = json.load(file)

        listado = []
        for blob in tracker.latest_message['entities']:
            print('blob:', blob['entity'])
            if blob['entity'] == 'topic':
                topic = blob['value']
                topic = unidecode.unidecode(topic)
                for x in datos:
                    add = True
                    for t in x['temas']:
                        for key in t['keywords']:
                            if topic in unidecode.unidecode(key) and add:
                                listado.append(x['nombre'] + ' - ' + key)
                                print("listado:",listado)
                                add = False
        
        if len(listado) != 0:
            dispatcher.utter_message(text=f"Ese tema aparece en los planes de gobierno de:")
            for partido in listado:
                dispatcher.utter_message(text=f"- {partido}")
        else:
            dispatcher.utter_message(text=f"Ninguno")
        dispatcher.utter_message(response="utter_add_task")
        slots = []
        slots.append(SlotSet("topic",None))
        return slots
        
class ActionAskElement(Action):
    def name(self)-> Text:
        return "action_ask_element"
    async def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
    
        print("===================================\n")
        print(tracker.latest_action_name)
        if(tracker.latest_action_name=="action_get_summarize" or tracker.latest_action_name=="action_get_keys"):
            dispatcher.utter_message(text=f"")
        elif (tracker.latest_action_name=="action_check_existence" and tracker.get_slot("partido")==None):
            dispatcher.utter_message(text=f"")
        else:
            if tracker.get_slot('partido')==None:
                dispatcher.utter_message(text=f"Me podrias especificar de que partido por favor. Existen 19")
            elif tracker.get_slot('tema')==None:
                dispatcher.utter_message(text=f"Me podrias especificar de que capitulo/tema por favor. Existen 7")
        return []

class ActionListElements(Action):
    partidos = Path("actions/partidos.txt").read_text().split("\n")
    temas = Path("actions/temas.txt").read_text().split("\n")
    def name(self) -> Text:
        return "action_list_elements"
    async def run(self, dispatcher: "CollectingDispatcher",
         tracker: Tracker, 
         domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot('partido')==None:
            dispatcher.utter_message(text=f"Los partidos politicos son los siguientes:")
            for p in self.partidos:
                dispatcher.utter_message(text=f"- {p}")
            dispatcher.utter_message(text=f"Escoge alguno")
        elif tracker.get_slot('tema')==None:
            dispatcher.utter_message(text=f"Los capitulos son los siguientes:")
            for t in self.temas:
                dispatcher.utter_message(text=f"- {t}")
            dispatcher.utter_message(text=f"Escoge alguno")
        return []

