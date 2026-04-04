#!/usr/bin/env python3
"""
Test delete stock function - verify HotDB data and cache clearing
"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

import requests
import time
from myquant.core.market.adapters import get_adapter

TEST_SYMBOL = '601628.SH'


def check_hotdb_data(symbol):
    """Check if stock data exists in HotDB"""
    print("\n[1] Checking HotDB data for %s..." % symbol)

    hotdb = get_adapter('hotdb')
    results = {}

    for period in ['1d', '1mon']:
        info = hotdb.get_data_info(symbol, period)
        has_data = info and info.get('has_data', False)
        results[period] = has_data

        if has_data:
            print("  [OK] %s: has %s items" % (period, info.get('count', 0)))
        else:
            print("  [EMPTY] %s: no data" % period)

    return results


def call_delete_api(symbol):
    """Call delete API to remove stock data"""
    print("\n[2] Calling API to delete %s..." % symbol)

    try:
        response = requests.delete(
            'http://localhost:8000/api/v5/hotdata/symbols/%s' % symbol
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("  [OK] API delete success")
                return True
            else:
                print("  [FAIL] API delete failed: %s" % result.get('error'))
                return False
        else:
            print("  [FAIL] API request failed: %s" % response.status_code)
            return False
    except Exception as e:
        print("  [ERROR] API call error: %s" % e)
        return False


def verify_data_cleared(symbol):
    """Verify HotDB data has been cleared"""
    print("\n[3] Verifying data cleared for %s..." % symbol)

    hotdb = get_adapter('hotdb')
    all_cleared = True

    for period in ['1d', '1mon']:
        info = hotdb.get_data_info(symbol, period)
        has_data = info and info.get('has_data', False)

        if has_data:
            print("  [FAIL] %s: data still exists!" % period)
            all_cleared = False
        else:
            print("  [OK] %s: data cleared" % period)

    return all_cleared


def verify_memory_cache_cleared(symbol):
    """Verify memory cache has been cleared"""
    print("\n[4] Verifying memory cache cleared for %s..." % symbol)

    hotdb = get_adapter('hotdb')
    cache_keys = list(hotdb._memory_cache.keys())
    symbol_keys = [k for k in cache_keys if k.startswith("%s:" % symbol)]

    if symbol_keys:
        print("  [FAIL] Memory cache still has keys: %s" % symbol_keys)
        return False
    else:
        print("  [OK] Memory cache cleared")
        return True


def run_test():
    """Run complete test"""
    print("=" * 70)
    print("Testing Delete Stock Function")
    print("=" * 70)

    # Step 1: Check initial state
    initial_state = check_hotdb_data(TEST_SYMBOL)
    has_any_data = any(initial_state.values())

    if not has_any_data:
        print("\n[WARNING] %s has no data in HotDB, please add it first" % TEST_SYMBOL)
        return

    # Step 2: Call delete API
    delete_success = call_delete_api(TEST_SYMBOL)
    if not delete_success:
        print("\n[STOP] API delete failed, stopping test")
        return

    # Wait for operation to complete
    time.sleep(1)

    # Step 3: Verify HotDB data cleared
    hotdb_cleared = verify_data_cleared(TEST_SYMBOL)

    # Step 4: Verify memory cache cleared
    memory_cleared = verify_memory_cache_cleared(TEST_SYMBOL)

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print("HotDB data cleared: %s" % ('YES' if hotdb_cleared else 'NO'))
    print("Memory cache cleared: %s" % ('YES' if memory_cleared else 'NO'))

    if hotdb_cleared and memory_cleared:
        print("\n[SUCCESS] All tests passed! Delete function works correctly")
    else:
        print("\n[FAILED] Some tests failed, please check the delete logic")


if __name__ == '__main__':
    run_test()
