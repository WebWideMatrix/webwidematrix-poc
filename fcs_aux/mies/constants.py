
# TODO consolidate with body constants
FLOOR_W = 200
FLOOR_H = 100

PROXIMITY = 10


DEFAULT_BLDG_ENERGY = 10
DEFAULT_RESIDENT_ENERGY = 100


# How far (in terms of bldgs) does smell reaches
SMELL_HORIZONTAL_OUTREACH = 100
SMELL_VERTICAL_OUTREACH = 0

# How much does the strength of smell decreases between each neighboring bldgs
SMELL_DECREASE_STEP = 1

GIVE_UP_ON_FLR = 20

# how much time (in seconds) to store a log of interactions
# for the calculation of a resident's interaction rate
INTERACTION_RATE_PERIOD = 5 * 60

# the threshold number of unique residents recently encountered
# that when exceeded will cause a resident to move to another flr
MAX_INTERACTION_RATE = 2


USER_CONTENT_TYPE = "user";

PERSONAL_TWITTER_FEED_DATA_PIPE = "PersonalTwitterFeed"

ACTIVE_STATUS = "active"
