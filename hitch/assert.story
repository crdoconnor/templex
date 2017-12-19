Simple string matching:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
    code: |
      Templex(u"The price is £200").assert_match(u"The price is £200")
  scenario:
    - Run code


Assert matching:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
      
      templex = Templex(u"My price is £{{ cost }}").with_vars(cost=r"[0-9]+")
  variations:
    Assert works:
      preconditions:
        code: |
          templex.assert_match(u"My price is £200")
      scenario:
        - Run code
    
    Assert fails different text py2:
      preconditions:
        code: |
          templex.assert_match(u"My price is £200.")
        python version: 2.7.10
      scenario:
        - Raises exception:
            exception type: exceptions.AssertionError
            message: |-
              ACTUAL:
              My price is £200.

              EXPECTED:
              My price is £{{ cost }}

              DIFF:
              - My price is £200.?                 -
              + My price is £200

              
    Assert fails different text py3:
      preconditions:
        code: |
          templex.assert_match(u"My price is £200.")
        python version: 3.5.0
      scenario:
        - Raises exception:
            exception type: builtins.AssertionError
            message: |-
              ACTUAL:
              My price is £200.

              EXPECTED:
              My price is £{{ cost }}

              DIFF:
              - My price is £200.?                 -
              + My price is £200
              
    Assert fails invalid regex py2:
      preconditions:
        code: |
          templex.assert_match(u"My price is £xxx")
        python version: 2.7.10
      scenario:
        - Raises exception:
            exception type: exceptions.AssertionError
            message: |-
              ACTUAL:
              My price is £xxx

              EXPECTED:
              My price is £{{ cost }}

              DIFF:
              - My price is £xxx+ My price is £{{ cost }}

              
    Assert fails invalid regex py3:
      preconditions:
        code: |
          templex.assert_match(u"My price is £xxx")
        python version: 3.5.0
      scenario:
        - Raises exception:
            exception type: builtins.AssertionError
            message: |-
              ACTUAL:
              My price is £xxx

              EXPECTED:
              My price is £{{ cost }}

              DIFF:
              - My price is £xxx+ My price is £{{ cost }}
