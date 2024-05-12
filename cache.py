from database import insert_one, insert_many, find_one, find_many, update_one, update_many, delete_one, delete_many
from typing import Any, Dict

cache: Dict[str, Dict[str, Any]] = {}


def cached(key: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Caches the provided data for the given key.
    If the key does not exist in the local database, it inserts the data.
    If the key exists in the cache, it returns the cached data.
    Otherwise, it caches the data and returns it.

    Args:
        key (str): The unique identifier for the data.
        data (Dict[str, Any]): The data to be cached.

    Returns:
        Dict[str, Any]: The cached data.
    """
    # Check if the key exists in the local database
    if find_one('users', {'id': key}) is None:
        # If not, insert the data into the local database
        result = insert_one('users', data)
        print(result)
    else:
        result = update_one('users', {'id': key}, data)
        print(result)
    # Check if the key exists in the cache
    if key in cache:
        return cache[key]
    else:
        # If not, cache the data and return it
        cache[key] = data
        return cache[key]


def init_cache() -> None:
    """
    Initializes the cache with data from the local database.
    Adds default values for 'req' and 'lang' keys.
    """
    users = find_many('users', {})
    for user in users:
        user_data = {
            key: user[key] for key in user
        }
        user_data['req'] = '@None'
        user_data['lang'] = 'English'
        cache[user['id']] = user_data
