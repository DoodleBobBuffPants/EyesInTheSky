# get function to test
from src.video_retrieval.MediaPlayer import MediaPlayer as Mp
from src.movement import FollowingDrone

# noinspection SpellCheckingInspection
testvid = "testvideo.mp4"  # test video - should use rtp://localhost:55004
mp = Mp()
drone = FollowingDrone()
mp.play_vid(testvid, drone)
