from io import TextIOWrapper
import json


class State:
    '''This class is responsible for managing a current or past state of an account.'''

    # ------------------------------------------------------------------------------
    def __init__(self, nonce: str, previous_reference: str, current_reference: str) -> None:
        # --------------------------------------------------------------------------
        """Initializes a State object"""
        # TODO Add Transaction class

        self.nonce = nonce
        self.previous_reference = previous_reference
        self.current_reference = current_reference

    # ------------------------------------------------------------------------------
    def to_JSON(self) -> str:
        # --------------------------------------------------------------------------
        """Returns a serialized version of a State object"""

        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    @classmethod
    # ------------------------------------------------------------------------------
    def from_JSON(self, JSON: str):
        # --------------------------------------------------------------------------
        """"Returns a State object given a JSON input. If JSON is not formatted
        correctly, this method will return None.
        """

        try:
            data = json.loads(JSON)
            if not isinstance(data, dict):
                raise ValueError

            state = State(nonce=data['nonce'], previous_reference=data['previous_reference'],
                          current_reference=data['current_reference'])
            return state
        except ValueError:
            print('State data is not a "dict".')
            return None
        except KeyError:
            print('State is not formatted correctly.')
            return None
        except:
            print('Unable to convert data in State object.')
            return None

    @classmethod
    # ------------------------------------------------------------------------------
    def from_File(self, file: TextIOWrapper):
        # --------------------------------------------------------------------------
        """"Returns a State object given a JSON input. If JSON is not formatted
        correctly, this method will return None.
        """

        try:
            data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError

            state = State(nonce=data['nonce'], previous_reference=data['previous_reference'],
                          current_reference=data['current_reference'])
            return state
        except ValueError:
            print('State data is not a "dict".')
            return None
        except KeyError:
            print('State is not formatted correctly.')
            return None
        except:
            print('Unable to convert data in State object.')
            return None
