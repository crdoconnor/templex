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
        message: |-
          'cost' not found in variables. Specify with with_vars(var=regex).

#Duplicate variables

