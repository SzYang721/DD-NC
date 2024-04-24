import sys
import wandb
from utils import *
import matplotlib.pyplot as plt
from Visualization import *

def AE_trainer(args, autoencoder, trainloader, epoch_id, criterion, optimizer, scheduler=None, visualize = False):

    losses = AverageMeter()

    if args.optimizer == 'LBFGS':
        print('\nTraining Epoch: [%d | %d]' % (epoch_id + 1, args.epochs))
    else:
        print('\nTraining Epoch: [%d | %d] LR: %f' % (epoch_id + 1, args.epochs, scheduler.get_last_lr()[-1]))
    
    if visualize:
        indices = random_sample_images_index(trainloader)

    for batch_idx, (inputs, targets) in enumerate(trainloader):

        inputs, targets = inputs.to(args.device), targets.to(args.device)

        autoencoder.train()
        outputs = autoencoder(inputs)
        
        loss = criterion(outputs, inputs).to(args.device)
        # loss = nn.functional.binary_cross_entropy(outputs,inputs,reduction="mean").to(args.device)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # measure accuracy and record loss
        autoencoder.eval()
        losses.update(loss.item(), inputs.size(0))
    
    print('[epoch: %d] (%d/%d) | Loss: %.4f |' %
          (epoch_id + 1, batch_idx + 1, len(trainloader), losses.avg))

    if 'wandb' in sys.modules:
        wandb.log({
            "losses.avg":losses.avg, 
            "LR":scheduler.get_last_lr()[-1]
        })

    if args.optimizer != 'LBFGS' and scheduler:
        scheduler.step()
    
    # Visualization check
    if visualize:  # Optionally visualize every 10 epochs
        inputs, labels = images_from_index(trainloader.dataset, indices)
        inputs, labels = inputs.to(args.device), labels.to(args.device)
        with torch.no_grad():
            # Taking a subset for visualization
            outputs = autoencoder(inputs)
            visualize_images(inputs.cpu(),labels.cpu(), True)
            visualize_images(outputs.cpu(),labels.cpu(), True)


def AE_train(args, model, trainloader, visualize = False):
    
    criterion = make_criterion_AE(args)
    optimizer = make_optimizer(args, model)
    scheduler = make_scheduler(args, optimizer)

    print('# of model parameters: ' + str(count_network_parameters(model)))
    print('--------------------- Training -------------------------------')
    for epoch_id in range(args.epochs):

        AE_trainer(args, model, trainloader, epoch_id, criterion, optimizer, scheduler, visualize = visualize)
        torch.save(model.decoder.state_dict(), args.save_path + "/epoch_" + str(epoch_id + 1).zfill(3) + ".pth")


#  if visualize:
#         channels, height, width = inputs[0].shape
#         fig, axs = plt.subplots(2, 1, figsize=(5, 10))
#         with torch.no_grad():
#             # Clear current axes
#             axs[0].clear()
#             axs[1].clear()
            
#             # Display original and reconstructed images
#             axs[0].imshow(inputs[0].cpu().view(height,width,channels).numpy())
#             axs[0].set_title("Original")
#             axs[0].axis('off')
            
#             axs[1].imshow(outputs[0].cpu().view(height,width,channels).numpy())
#             axs[1].set_title("Reconstructed")
#             axs[1].axis('off')
            
#             # Draw the updated plot
#             plt.draw()
#             plt.pause(0.001)  # Pause briefly to update plots