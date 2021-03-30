* There are other measuring and weighing devices in the market, and
  this module just considers Zippcube but contains many code and
  interfaces that can be reused for other devices. Extract the common
  pieces into a new, generic module, and make this one contain only
  the specifics for Zippcube, and depend on the generic module for
  the common parts.
