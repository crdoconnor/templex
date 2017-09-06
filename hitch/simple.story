Match price sentence:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
      
      templex = Templex("The price is £{{ cost }}").with_vars(cost=r"[0-9]+")
      
      match = templex.match("The price is £200")
    code: match['cost']
  scenario:
    - Should be equal to: |
        "200"
