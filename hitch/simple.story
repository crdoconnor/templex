Price sentence:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
      
      templex = Templex("The price is £{{ cost }}").with_vars(cost=r"[0-9]+")

  variations:
    Get price back:
      preconditions:
        code: templex.match("The price is £200")['cost']
      scenario:
        - Should be equal to: |
            "200"

    Non-matching string:
      preconditions:
        code: templex.match("The price is 200") is None
      scenario:
        - Should be equal to: True

        
No matching variables:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
      
      templex = Templex("The price is £{{ cost }}")
    code: |
      templex.match("The price is £{{ cost }}")
  scenario:
    - Raises exception:
        exception type: templex.exceptions.KeyNotFound
        message: |
          'cost' not found in variables. Specify with with_vars(var=regex).

#Duplicate variables

Assert matching:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
      
      templex = Templex("The price is £{{ cost }}").with_vars(cost=r"[0-9]+")
    code: |
      templex.assert_match("The price is £{{ cost }}.")
  variations:
    Assert works:
      scenario:
        - Run code
    
    #Assert fails:
      #code: |
        #templex.assert_match("The price is £{{ cost }}")
      #scenario:
