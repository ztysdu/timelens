import lpips
import torch
from torch import nn

from torch.nn import functional as F
from torch.autograd import Variable
from math import exp

def gaussian(window_size,sigma):
    gauss = torch.Tensor([exp(-(x - window_size // 2) ** 2 / float(2 * sigma ** 2)) for x in range(window_size)])
    return gauss/torch.sum(gauss)  

def create_window(window_size,channel=1):
    _1D_window = gaussian(window_size, 1.5).unsqueeze(1)  # window_size,1
    _2D_window = _1D_window.mm(_1D_window.t()).float().unsqueeze(0).unsqueeze(0)
    # 1,1,window_size,_window_size->channel,1,window_size,_window_size
    window = Variable(_2D_window.expand(channel, 1, window_size, window_size).contiguous())
    return window


def _ssim(img1, img2, window, window_size, channel, size_average=True):
    mu1 = F.conv2d(img1, window, padding=window_size // 2, groups=channel)
    mu2 = F.conv2d(img2, window, padding=window_size // 2, groups=channel)

    mu1_sq = mu1.pow(2)
    mu2_sq = mu2.pow(2)
    mu1_mu2 = mu1 * mu2

    sigma1_sq = F.conv2d(img1 * img1, window, padding=window_size // 2, groups=channel) - mu1_sq
    sigma2_sq = F.conv2d(img2 * img2, window, padding=window_size // 2, groups=channel) - mu2_sq
    sigma12 = F.conv2d(img1 * img2, window, padding=window_size // 2, groups=channel) - mu1_mu2

    C1 = 0.01 ** 2
    C2 = 0.03 ** 2

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))

    if size_average:
        return ssim_map.mean()
    else:
        return ssim_map.mean(1).mean(1).mean(1)


class SSIM(torch.nn.Module):
    def __init__(self, window_size=11, size_average=True):
        super(SSIM, self).__init__()
        self.window_size = window_size
        self.size_average = size_average
        self.channel = 1
        self.window = create_window(window_size, self.channel)

    def forward(self, img1, img2):
        (_, channel, _, _) = img1.size()

        if channel == self.channel and self.window.data.type() == img1.data.type():
            window = self.window
        else:
            window = create_window(self.window_size, channel)

            if img1.is_cuda:
                window = window.cuda(img1.get_device())
            window = window.type_as(img1)

            self.window = window
            self.channel = channel

        return _ssim(img1, img2, window, self.window_size, channel, self.size_average)

class Total_loss_color(nn.Module):

    def __init__(self, device, v=0.1):
        super(Total_loss_color, self).__init__()
        self.v = v
        self.device = device
        self.loss_perc = lpips.LPIPS(net='vgg').to(self.device)
        self.loss_mae = torch.nn.L1Loss()

    def forward(self, truth_img, pre_img):

        loss_pre = self.v * torch.mean(self.loss_perc(pre_img, truth_img, normalize=True)) + self.loss_mae(pre_img,  truth_img)

        return loss_pre

class Total_loss_color_Iteration(nn.Module):

    def  __init__(self, device, v=0.1):
        super(Total_loss_color_Iteration, self).__init__()
        self.v = v
        self.device = device
        self.loss_perc = lpips.LPIPS(net='vgg').to(self.device)
        self.loss_mae = torch.nn.L1Loss()
        self.SSIM_lossFn = SSIM()

    def forward(self, truth_img_list, pre_img_list):
        total_loss = 0.0
        for i in range(len(truth_img_list)):
            pre_img = pre_img_list[i].to(self.device)
            truth_img = truth_img_list[i].to(self.device)

            loss = self.v * torch.mean(self.loss_perc(pre_img, truth_img, normalize=True)) + self.loss_mae(pre_img,truth_img) + 0.5 * (1 - self.SSIM_lossFn(pre_img, truth_img))

            total_loss = total_loss + loss

        return total_loss / len(truth_img_list)