Simple string matching:
  based on: templex
  steps:
  - Run: |
      from templex import Templex 
      Templex(u"The price is £200").assert_match(u"The price is £200")


Assert matching:
  based on: templex
  given:
    setup: |
      from templex import Templex
      
      templex = Templex(u"My price is £{{ cost }}").with_vars(cost=r"[0-9]+")
  variations:
    Assert works:
      steps:
        - Run: |
            templex.assert_match(u"My price is £200")
    
    Assert fails different text py2:
      given:
        python version: 2.7.10
      steps:
        - Run:
            code: templex.assert_match(u"My price is £200.")
            raises:
              type: builtins.AssertionError
              message: |-
                ACTUAL:
                My price is £200.

                EXPECTED:
                My price is £{{ cost }}

                DIFF:
                - My price is £200.?                 -
                + My price is £200

              
    Assert fails different text py3:
      given:
        python version: 3.5.0
      steps:
        - run:
            code: |
              templex.assert_match(u"My price is £200.")
            raises:
              type: builtins.AssertionError
              message: |-
                ACTUAL:
                My price is £200.

                EXPECTED:
                My price is £{{ cost }}

                DIFF:
                - My price is £200.?                 -
                + My price is £200
              
    Assert fails invalid regex py2:
      given:
        python version: 2.7.10
      steps:
        - run:
            code: |
              templex.assert_match(u"My price is £xxx")
            raises:
              type: builtins.AssertionError
              message: |-
                ACTUAL:
                My price is £xxx

                EXPECTED:
                My price is £{{ cost }}

                DIFF:
                - My price is £xxx+ My price is £{{ cost }}

              
    Assert fails invalid regex py3:
      given:
        python version: 3.5.0
      steps:
        - run:
            code: |
              templex.assert_match(u"My price is £xxx")
            raises:
              type: builtins.AssertionError
              message: |-
                ACTUAL:
                My price is £xxx

                EXPECTED:
                My price is £{{ cost }}

                DIFF:
                - My price is £xxx+ My price is £{{ cost }}
