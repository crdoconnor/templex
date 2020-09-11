Get price back:
  steps:
  - Run: |
      from templex import Templex
        
      templex = Templex(u"The price is £{{ cost }}").with_vars(cost=r"[0-9]+")
      assert templex.match(u"The price is £200")['cost'] == "200"

Non-matching string:
  steps:
  - run: |
      from templex import Templex
        
      templex = Templex(u"The price is £{{ cost }}").with_vars(cost=r"[0-9]+")
      assert templex.match(u"The price is 200") is None
