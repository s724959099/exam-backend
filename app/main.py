


def connect_to_next_port(minimum: int) -> int:
    """Connects to the next available port.

    Args:
      minimum: A port value greater or equal to 1024.

    Returns:
      The new minimum port.
    """
    assert minimum >= 1024, 'Minimum port must be at least 1024.'
    port = minimum
    assert port is not None
    return port


if __name__ == '__main__':
    print('123')
