Assert matching:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
      
      templex = Templex("The price is £{{ cost }}").with_vars(cost=r"[0-9]+")
    code: |
      templex.assert_match("The price is £200")
  variations:
    Assert works:
      scenario:
        - Run code
    
    Assert fails:
      preconditions:
        code: |
          templex.assert_match("The price is £")
      scenario:
        - Raises exception:
            exception type: templex.exceptions.NonMatching
