No matching variables:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
      
      templex = Templex(u"The price is £{{ cost }}")
    code: |
      templex.match(u"The price is £{{ cost }}")
  scenario:
    - Raises exception:
        exception type: templex.exceptions.KeyNotFound
        message: |-
          'cost' not found in variables. Specify with with_vars(var=regex).

Values must be strings:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
    code: |
      Templex(u"The price is £200".encode('utf8'))
  scenario:
    - Raises exception:
        exception type: templex.exceptions.MustUseString
        message: Must use string with templex (e.g. not bytes).


  variations:
    Normal Match:
      preconditions:
        code: |
          Templex(u"The price is £200").match(u"The price is £200".encode('utf8'))

    Assert match:
      preconditions:
        code: |
          Templex(u"The price is £200").assert_match(u"The price is £200".encode('utf8'))
          
