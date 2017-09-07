Assert matching:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
      
      templex = Templex("The price is £{{ cost }}").with_vars(cost=r"[0-9]+")
  variations:
    Assert works:
      preconditions:
        code: |
          templex.assert_match("The price is £200")
      scenario:
        - Run code
    
    Assert fails different text:
      preconditions:
        code: |
          templex.assert_match("My price is £200")
      scenario:
        - Raises exception:
            exception type: templex.exceptions.NonMatching
            message: |
              ACTUAL:
              My price is £200

              EXPECTED:
              The price is £{{ cost }}

              DIFF:
              - My price is £200? ^^
              + The price is £200? ^^^

    Assert fails invalid regex:
      preconditions:
        code: |
          templex.assert_match("The price is £xxx")
      scenario:
        - Raises exception:
            exception type: templex.exceptions.NonMatching
            message: |-
              ACTUAL:
              The price is £xxx

              EXPECTED:
              The price is £{{ cost }}

              DIFF:
              - The price is £xxx+ The price is £{{ cost }}

