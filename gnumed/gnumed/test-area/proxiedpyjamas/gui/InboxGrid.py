_indicator = {
    -1: '',
    0: '',
    1: '*!!*'
}

def fill_grid_messages(grid, messages):
    """ fills in inbox messages into a grid
    """
    if messages is None:
        messages = []
    grid.resize(1+len(messages), 5)
    for (row, item) in enumerate(messages):
        grid.setHTML(row+1, 0, _indicator[item.importance])
        grid.setHTML(row+1, 1, str(item.received_when))
        grid.setHTML(row+1, 2, item.category)
        grid.setHTML(row+1, 3, item.type)
        grid.setHTML(row+1, 4, item.comment)

