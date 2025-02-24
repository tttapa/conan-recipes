#include <iostream>
#include <torch/torch.h>

int main() {
  auto tensor = sqrt(2 * torch::eye(3, torch::device(torch::kCUDA)));
  std::cout << tensor << std::endl;
}
