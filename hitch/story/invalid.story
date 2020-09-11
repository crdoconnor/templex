No matching variables:
  based on: templex
  given:
    setup: |
      from templex import Templex
      
      templex = Templex(u"The price is £{{ cost }}")
  steps:
  - run:
      code: templex.match(u"The price is £{{ cost }}")
      raises:
        type: templex.exceptions.KeyNotFound
        message: |-
          'cost' not found in variables. Specify with with_vars(var=regex).

Values must be strings:
  based on: templex
  given:
    setup: |
      from templex import Templex
      
  steps:
  - run:
      code: |
        templex.match(Templex(u"The price is £200".encode('utf8')))
      raises:
        type: templex.exceptions.MustUseString
        message: Must use string with templex (e.g. not bytes).


  variations:
    Normal Match:
      given:
        setup: |
          Templex(u"The price is £200").match(u"The price is £200".encode('utf8'))

    Assert match:
      given:
        setup: |
          Templex(u"The price is £200").assert_match(u"The price is £200".encode('utf8'))
          
