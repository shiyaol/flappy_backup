import argparse
import torch
import cv2
from src.deep_q_network import DeepQNetwork
from src.flappy_bird_wenkai import FlappyBird
from src.utils import pre_processing
import os
#os.environ["SDL_VIDEODRIVER"] = "dummy"

file = open("test_score.txt", "w")

def get_args():
    parser = argparse.ArgumentParser(
        """Implementation of Deep Q Network to play Flappy Bird""")
    parser.add_argument("--image_size", type=int, default=84, help="The common width and height for all images")
    parser.add_argument("--saved_path", type=str, default="trained_models-all")

    args = parser.parse_args()
    print(args)
    return args


def test_flap(opt):
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)

    model = torch.load("{}/flappy_bird_final_backup".format(opt.saved_path), map_location=lambda storage, loc: storage)
    model.eval()
    game_state = FlappyBird()
    image, reward, terminal = game_state.next_frame(0)
    file.write(str(game_state.score) + '\n')
    image = pre_processing(image[:game_state.screen_width :int(game_state.base_y)], opt.image_size, opt.image_size)
    image = torch.from_numpy(image)
    if torch.cuda.is_available():
        model.cuda()
        image = image.cuda()
    state = torch.cat(tuple(image for _ in range(4)))[None, :, :, :]

    while 1:

        prediction = model(state)
        action = torch.argmax(prediction)

        next_image, reward, terminal = game_state.next_frame(action)
        #print(reward)
        if (reward == 1): print(game_state.score)
        next_image = pre_processing(next_image[:game_state.screen_width, :int(game_state.base_y)], opt.image_size,
                                    opt.image_size)
        next_image = torch.from_numpy(next_image)
        if torch.cuda.is_available():
            next_image = next_image.cuda()
        next_state = torch.cat((state[0, 1:, :, :], next_image))[None, :, :, :]

        state = next_state
        if terminal:
            file.write(str(game_state.score) + '\n')
            break


if __name__ == "__main__":
    args = get_args()
    test_flap(args)
