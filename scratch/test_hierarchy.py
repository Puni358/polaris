import highspy
import numpy as np

# Let's test Highs multi-objective priorities:
# If we have priorities:
# J1: 6, J_NC: 5, J2: 4, J3: 3, J4: 2, J_tie: 1
# Does J4 come before J_tie?
# In HiGHS: higher priority number is optimized first!
# So priority 6 (J1) > 5 (J_NC) > 4 (J2) > 3 (J3) > 2 (J4) > 1 (J_tie).
# Let's verify that J4 is indeed optimized BEFORE J_tie with this priority assignment.
