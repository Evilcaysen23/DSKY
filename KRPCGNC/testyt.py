import krpc
import time
conn = krpc.connect(name='SpeedCheck')
vessel = conn.space_center.active_vessel
flight = vessel.flight(vessel.reference_frame)
#get vertical speed and print use non_rotating_reference_frame

reference_frame = create_relative(reference_frame[, position = (0.0, 0.0, 0.0)][, rotation = (0.0, 0.0, 0.0, 1.0)][, velocity = (0.0, 0.0, 0.0)][, angular_velocity = (0.0, 0.0, 0.0)])

def get_vertical_speed():
    return flight.vertical_speed


def main():
    while True:
        vertical_speed = get_vertical_speed()
        print(f"Vertical Speed: {vertical_speed:.2f} m/s")
        time.sleep(1)  # Update every second
if __name__ == "__main__":
    get_vertical_speed()
    main()