# dialog_framework
This is the implementation of client-server communication of [Eva: an open-domain chinese dialogue system with large-scale generative pre-training](https://arxiv.org/abs/2108.01547).

The data structure received from the front end
data: {
    'sentence': str,
    'length': int(optional),
    'top-k': int(optional) 
}
