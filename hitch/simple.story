Price sentence:
  based on: templex
  preconditions:
    setup: |
      from templex import Templex
      
      templex = Templex(u"The price is £{{ cost }}").with_vars(cost=r"[0-9]+")

  variations:
    Get price back:
      preconditions:
        code: templex.match(u"The price is £200")['cost']
      scenario:
        - Should be equal to: |
            "200"

    Non-matching string:
      preconditions:
        code: templex.match(u"The price is 200") is None
      scenario:
        - Should be equal to: True
