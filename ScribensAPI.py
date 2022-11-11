from __future__ import annotations
from typing import List, Dict, Tuple, Optional, Union, Any
from ast import literal_eval

from pprint import pprint
import json

import requests as rq

from fake_useragent import UserAgent
from utils import *

ua = UserAgent()


class TextLengthError(Exception) : pass


class ScribensAPI:
    """Class describing an interface for Scribens.fr's API.
    Mostly used to spellcheck texts using python.
    """

    check_url = "https://www.scribens.fr/Scribens/TextSolution_Servlet"
    CHAR_LIMIT = 6000


    @classmethod
    def spellcheck_text(cls, txt:str) -> str:
        """Checks the spelling of a text in french

        Args:
            txt (str): The text to check

        Returns:
            str: Checked text
        """          
        
        return cls._check_text(txt) if len(txt) <= cls.CHAR_LIMIT else cls._check_long_text(txt)


    @classmethod
    def _check_text(cls, txt:str) -> str:
        f"""Spellchecks a text

        Args:
            txt (str): Text to spellcheck, shorter than {cls.CHAR_LIMIT} characters

        Returns:
            str: Spellchecked text
        
        Raises:
            TextLengthError: Your text is too long for this method
        """

        if len(txt) > cls.CHAR_LIMIT : raise TextLengthError(f"Please use ScribensAPI.check_long_text to chekc texts longer than {cls.CHAR_LIMIT} characters.")

        txt = txt.strip()
        data = cls.request_check(txt)

        misspells = ScribenMisspell.get_solutions_from_json(data)
        
        # Sorts misspells from last to first, to not modify misspell position when correcting text
        misspells.sort(key=lambda m: m.position[1], reverse=True)     
        
        for m in misspells:  
            txt_to_insert = m.annotation
            if m.solution :
                if m.solution.strip() :
                    txt_to_insert = m.solution
            
            line = get_line(txt, m.line)
            corrected_line = insert_after(line, m.position[1], f" {{{txt_to_insert.lower()}}}")
            
            txt = replace_line(txt, m.line, corrected_line)
            
            print(f"Texte:\n\t{txt}\nErreur:\n\t{m.solution}\n")

        return txt


    @classmethod
    def _check_long_text(cls, txt:str) -> str:
        f"""Spellchecks a text

        Args:
            txt (str): Text to spellcheck, longer than {cls.CHAR_LIMIT} characters.

        Returns:
            str: Spellchecked text
        
        Raises:
            TextLengthError: Your text is too short for this method
        """
        
        if len(txt) <= cls.CHAR_LIMIT : raise TextLengthError(f"Please use ScribensAPI.check_text to chekc texts shorter than {cls.CHAR_LIMIT} characters.")

        

    @classmethod
    def request_check(cls, txt:str) -> List[Dict]:
        """Requests spellcheck to Scribens

        Args:
            txt (str): Text to check

        Returns:
            List[Dict]: List of errors in the text
        """
        
        headers = {'User-Agent' : ua.chrome}
        r = rq.post(cls.check_url, data=cls.generate_check_request_payload(txt), headers=headers)
        print(r.headers)
        
        with open("response.json", "w") as f:
            json.dump(r.json(), f , indent=2)
        
        return r.json()


    @classmethod
    def generate_check_request_payload(cls, txt:str) -> dict:
        """Generates the payload for the spell request

        Args:
            txt (str): Text to spellcheck

        Returns:
            dict: The correct payload for spellcheck request
        """

        formattedText = ""
        for line in txt.split("\n"):
            formattedText += f"<p>{line}</p>"

        return {
            "FunctionName": "GetTextSolution",
            "texteHTML": formattedText,
            #"texteStat": ,
            "IdMax": 0,
            "IdMaxSousGroupeRep": 0,
            "writeRequest": False,
            "cntRequest30": 1,
            "firstRequest": True,
            "progression": 0,
            "charPrecPh": -1,
            "optionsCor": "Genre_Je:0|Genre_Tu:0|Genre_Nous:0|Genre_Vous:0|Genre_On:0|RefOrth:0|ShowUPSol:1",
            "optionsStyle": "RepMin:3|GapRep:3|AllWords:0|FamilyWords:0|MinPhLg:30|MinPhCt:5|Ttr:250|Tts:150",
            #"ensIdRepetitions": ,
            "corSt": False,
            "plugin": False,
            #"identifier": ,
            #"password": ,
            "langId": "fr",
            "isSampleText": False,
            "modePlugin": None
        }


class ScribenMisspell:
    """Describes a misspell in a texte as given by Scribens
    """


    def __init__(self, line:int,  position:Tuple[int, int], solution:str | None, annotation:Optional[str]) -> None:
        self.position = position
        self.solution = solution
        self.annotation = annotation
        self.line = line


    @classmethod
    def get_solutions_from_json(cls, data:dict) -> List[ScribenMisspell]:
        """Creates a ScribenMisspell from JSON response to ScribensAPI.request_check

        Args:
            data (dict): JSON response

        Returns:
            ScribenMisspell: ScribenMisspell generated from JSON response
        """

        solutions : List[ScribenMisspell] = []

        data_solutions : dict = data["SolutionCor"]["MapMotSolution"]

        for misspell in data_solutions.values():
            solutions.append(cls.from_json(misspell))
        
        return solutions


    @classmethod
    def from_json(cls, data:Dict[str, Any]) -> ScribenMisspell:
        position : Tuple[int, int] = (data["Start_Pos"], data["End_Pos"])

        line = literal_eval(data["IdPhrase"].removeprefix('p'))
        print(f"Line : {line}")
        vectSolution = data["vectSolution"]
        solution = vectSolution[0]['Left'] if vectSolution else None
        
        raw_explanation = data["ExplicationSolution"]
        explanation = get_first_sentence(remove_tags(raw_explanation))

        return ScribenMisspell(line, position, solution, explanation)
    

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} pos={self.position} solution={self.solution}>"
    
    def __repr__(self) -> str:
        return self.__str__()
