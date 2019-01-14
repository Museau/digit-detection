import argparse
from tqdm import tqdm
import time

import torch

from utils.dataloader import prepare_dataloaders


def test_model(model, test_loader, device,
               ):
    since = time.time()
    model = model.to(device)
    model = model.eval()

    #  optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    #  loss_ndigits = torch.nn.CrossEntropyLoss()

    print("# Testing Model ... #")
    test_correct = 0
    test_n_samples = 0
    y_true = []
    y_pred = []
    for i, batch in enumerate(tqdm(test_loader)):
        # get the inputs
        inputs, targets = batch['image'], batch['target']

        inputs = inputs.to(device)

        target_ndigits = targets[:, 0].long()
        target_ndigits = target_ndigits.to(device)

        # Forward
        outputs = model(inputs)

        #  loss = loss_ndigits(outputs, target_ndigits)

        # Statistics
        #  test_loss += loss.item()
        #  test_n_iter += 1
        _, predicted = torch.max(outputs.data, 1)

        y_pred.extend(list(predicted.numpy()))
        y_true.extend(list(target_ndigits.numpy()))

        test_correct += (predicted == target_ndigits).sum().item()
        test_n_samples += target_ndigits.size(0)
        test_accuracy = test_correct / test_n_samples

    from sklearn.metrics import confusion_matrix

    print("Confusion Matrix")
    print("===============================")
    print(confusion_matrix(y_true, y_pred, labels=range(0, 7)))
    print("===============================")
    print('\n\nTest Set Accuracy: {:.4f}'.format(test_accuracy))

    time_elapsed = time.time() - since

    print('\n\nTesting complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default='data/SVHN')
    parser.add_argument("--results_dir", type=str, default='results')
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--sample_size", type=int, default=None)
    parser.add_argument("--dataset_split", type=str, default='test')
    parser.add_argument("--model_filename", type=str)

    args = parser.parse_args()
    batch_size = args.batch_size
    datadir = args.data_dir
    sample_size = args.sample_size
    results_dir = args.results_dir
    dataset_split = args.dataset_split
    model_filename = args.model_filename

    test_loader = prepare_dataloaders(dataset_split=dataset_split,
                                      batch_size=batch_size,
                                      sample_size=sample_size,
                                      datadir=datadir)

    (train_loader,
     valid_loader) = prepare_dataloaders(dataset_split='train',
                                         batch_size=batch_size,
                                         sample_size=100,
                                         datadir=datadir)

    # Define model architecture

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("Device used: ", device)

    model = torch.load(model_filename, map_location=device)

    test_model(model,
               test_loader=test_loader,
               device=device)
