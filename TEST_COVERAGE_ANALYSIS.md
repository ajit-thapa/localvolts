# Test Coverage Analysis - Localvolt HA Integration

## Executive Summary

**Current Test Coverage: 0%**

The Localvolt HA Integration has no automated tests. This analysis identifies critical gaps and proposes a prioritized testing roadmap to improve reliability and prevent regressions.

---

## Coverage Overview by Module

### 1. `const.py` - Constants & Validation Functions
**Current Coverage: 0%**

This module contains three critical input validation functions that are **completely untested**.

#### Functions Not Covered:
- `validate_api_key(key: str) -> bool`
- `validate_partner_id(pid: str) -> bool`  
- `validate_nmi_id(nmi: str) -> bool`

#### Why This is Critical:
- These functions are the **first line of defense** against invalid configuration
- Invalid inputs are silently accepted, creating confusing user experiences
- The `validate_nmi_id()` function has specific business logic (10 alphanumeric chars) that needs thorough testing

#### Test Cases Needed:
**validate_api_key:**
- Empty string → False
- Whitespace-only string → False
- Valid non-empty string → True
- String with leading/trailing whitespace → True (after strip)

**validate_partner_id:**
- Empty string → False
- Whitespace-only string → False
- Valid non-empty string → True
- String with leading/trailing whitespace → True (after strip)

**validate_nmi_id:**
- Less than 10 characters → False
- More than 10 characters → False
- Exactly 10 characters, all numeric → True
- Exactly 10 characters, all alphanumeric (including letters) → True
- Exactly 10 characters with special characters → False
- Lowercase letters → True (after uppercase conversion)
- Mixed case → True (case-insensitive)
- Whitespace in input → True (after strip)
- Empty string → False
- Whitespace-only string → False

---

### 2. `config_flow.py` - Configuration UI Flow
**Current Coverage: 0%**

The config flow handles user input and validation through the Home Assistant UI—critical for first-time setup and credential updates.

#### Classes & Methods Not Covered:
- `LocalvoltsMonitorConfigFlow.async_step_user()`
- `LocalvoltsMonitorOptionsFlowHandler.async_step_user()`
- `LocalvoltsMonitorOptionsFlowHandler.async_step_init()`
- `build_data_schema()`

#### Why This is Critical:
- Config flows directly affect user experience during setup
- Invalid states (e.g., missing validators) silently fail
- Edge cases like pre-filled values, error handling, and form validation are not validated

#### Test Cases Needed:
**build_data_schema:**
- Default schema generation (empty existing_data)
- Schema with existing data pre-filled
- Schema field requirements and types

**async_step_user (ConfigFlow):**
- Valid input creates entry with correct title
- Invalid API key shows error and re-displays form
- Invalid Partner ID shows error and re-displays form
- Invalid NMI ID shows error and re-displays form
- Multiple validation errors reported together
- Existing entry detection (single entry per config)
- Title uses uppercase NMI ID

**Options Flow:**
- async_step_init delegates to async_step_user
- User input is persisted as options
- Form displays existing options as defaults

---

### 3. `coordinator.py` - Data Fetching & Processing
**Current Coverage: 0%**

The coordinator handles all API communication and timestamp processing—critical for reliability and data accuracy.

#### Classes & Methods Not Covered:
- `LocalvoltsMonitorCoordinator._async_update_data()`
- `LocalvoltsMonitorCoordinator._process_timestamps()`
- Initialization and state management

#### Why This is Critical:
- **Network errors** are a real concern; the code catches them but behavior isn't verified
- **API errors** (401, 403) must be handled gracefully with meaningful messages
- **Timestamp parsing** has complex timezone logic that easily breaks with edge cases
- **Empty responses** are handled silently—behavior needs validation
- **State management** (interval_end, last_update, time_past_start) is critical for sensor accuracy

#### Test Cases Needed:
**_async_update_data:**
- Successful API call returns data correctly
- 401 (unauthorized) raises UpdateFailed with "Invalid API key" message
- 403 (forbidden) raises UpdateFailed with "Invalid Partner ID" message
- Network timeout raises UpdateFailed with appropriate message
- Connection error raises UpdateFailed with appropriate message
- Empty list response keeps previous data unchanged
- Empty dict response keeps previous data unchanged
- Non-list response keeps previous data unchanged
- First interval in list is used when multiple returned
- API response with missing keys still returns data (degrades gracefully)

**_process_timestamps:**
- ISO format timestamp with timezone info parsed correctly
- ISO format timestamp without timezone defaults to UTC
- intervalEnd and lastUpdate stored correctly
- time_past_start calculated correctly (last_update - interval_start)
- Malformed timestamp raises error and logs message (no exception propagation)
- Missing intervalEnd key logs error and continues
- Missing lastUpdate key logs error and continues
- Different timezone formats handled consistently

**Coordinator initialization:**
- API key, partner_id, nmi_id stored correctly
- Initial data is empty dict
- SCAN_INTERVAL is 20 seconds
- Coordinator name is "Localvolts Monitor"

---

### 4. `sensor.py` - Sensor Entities
**Current Coverage: 0%**

Sensor classes convert raw API data into Home Assistant sensor entities.

#### Classes & Methods Not Covered:
- `LocalvoltsNumericSensor.native_value` (data conversion and caching)
- `LocalvoltsDataLagSensor.native_value` (duration calculation)
- `LocalvoltsIntervalEndSensor.native_value` (timestamp passthrough)
- `LocalvoltsLastUpdateSensor.native_value` (timestamp passthrough)
- `LocalvoltsQualitySensor.native_value` (enum value)
- `async_setup_entry()` (entity creation and registration)

#### Why This is Critical:
- **Sensor values directly affect automation logic**—wrong calculations cause incorrect behavior
- **Caching logic** ensures users see last-known value on API failures
- **Type conversions** (string → float) can silently fail
- **Unit conversions** (multiplication by factors) must be exact
- Sensor initialization affects device grouping and entity IDs

#### Test Cases Needed:
**LocalvoltsNumericSensor.native_value:**
- Valid numeric string converted correctly with factor applied
- "N/A" string returns cached value (fallback)
- None value returns cached value (fallback)
- Invalid numeric string returns cached value (fallback)
- First valid value updates cache
- Subsequent calls use updated cache
- Factor 0.01 applied to price values (converts cents to dollars)
- Factor 0.001 applied to energy values (converts to kWh)
- Factor 1 passed through unchanged
- Zero returns zero (not treated as falsy)
- Negative values allowed (can export at negative price)

**LocalvoltsDataLagSensor.native_value:**
- Returns None when time_past_start is None
- Converts timedelta to total_seconds()
- Accuracy (seconds precision)

**Timestamp sensors:**
- Returns coordinator's timestamp values unchanged
- Returns None when timestamp not yet set

**LocalvoltsQualitySensor.native_value:**
- Returns "Act" when in coordinator data
- Returns "Exp" when in coordinator data
- Returns "Fcst" when in coordinator data
- Returns None when not in data

**async_setup_entry:**
- Creates 17 numeric sensors from SENSOR_DEFINITIONS
- Creates 1 data lag sensor
- Creates 1 interval end sensor
- Creates 1 last update sensor
- Creates 1 quality sensor
- Total: 21 sensors created
- All entities registered with async_add_entities
- All sensors have unique_ids
- All sensors have correct device_info with NMI

---

### 5. `__init__.py` - Integration Lifecycle
**Current Coverage: 0%**

The integration setup and teardown orchestrates coordinator initialization and platform setup.

#### Functions Not Covered:
- `async_setup_entry()`
- `async_unload_entry()`

#### Why This is Critical:
- **Setup failures** can leave integrations in broken states
- **Coordinator initialization** must complete before sensors are created
- **Data cleanup** on unload prevents memory leaks

#### Test Cases Needed:
**async_setup_entry:**
- Coordinator initialized with correct credentials
- Coordinator's async_config_entry_first_refresh() is awaited
- Coordinator stored in hass.data[DOMAIN][entry_id]
- Sensor platform is set up
- Returns True on success
- Handles coordinator initialization errors

**async_unload_entry:**
- Platforms are unloaded
- Coordinator removed from hass.data on successful unload
- Returns True when unload_platforms returns True
- Returns False when unload_platforms returns False
- No error when entry not in hass.data

---

## Priority Matrix

### 🔴 **Critical** (Must have)
These are foundational and prevent data corruption or crashes:
1. **Validation functions** (const.py) - Input validation is the foundation
2. **Coordinator._async_update_data()** - All data flows through here
3. **Coordinator._process_timestamps()- Complex timezone logic prone to errors
4. **LocalvoltsNumericSensor.native_value** - Directly affects automations
5. **async_setup_entry()** - Integration won't load without correct setup

### 🟡 **High** (Should have)
These prevent subtle bugs and improve reliability:
1. **Config flow validation** - User experience and error handling
2. **Timestamp sensors** - Depend on coordinator state
3. **async_unload_entry()** - Resource cleanup
4. **LocalvoltsQualitySensor** - Important for automations

### 🟢 **Medium** (Nice to have)
These improve code confidence but have lower impact:
1. **LocalvoltsDataLagSensor** - Diagnostic sensor
2. **async_setup_entry** platform setup validation

---

## Testing Approach Recommendation

### 1. **Use `pytest` for unit tests**
   - Home Assistant has `homeassistant.core` mocking utilities
   - Industry standard for Python projects
   - Good coverage reporting with pytest-cov

### 2. **Setup Structure**
   ```
   tests/
   ├── conftest.py              # Shared fixtures
   ├── test_const.py            # Validation functions
   ├── test_config_flow.py      # Config UI
   ├── test_coordinator.py      # Data fetching (needs async/http mocking)
   ├── test_sensor.py           # Sensor entities
   └── test_integration.py      # Setup/teardown
   ```

### 3. **Mock External Dependencies**
   - `aiohttp.ClientSession.get()` - Mock API calls
   - `dateutil.parser.isoparse()` - Already pure; test directly
   - Home Assistant entities - Use mock coordinator

### 4. **Key Tools**
   - `pytest-asyncio` - Async function testing
   - `unittest.mock.Mock`, `MagicMock` - Mock external APIs
   - `pytest-aiohttp` - HTTP mocking helpers (optional)

### 5. **Test File Template**
   ```python
   import pytest
   from unittest.mock import Mock, AsyncMock, patch
   from custom_components.localvolts_monitor.const import validate_nmi_id

   def test_validate_nmi_id_valid():
       assert validate_nmi_id("4103XXXXXX") is True
       
   def test_validate_nmi_id_short():
       assert validate_nmi_id("410") is False
   ```

---

## Estimated Test Writing Effort

| Module | # Test Cases | Estimated Time |
|--------|-------------|-----------------|
| const.py | 13 | 30 mins |
| config_flow.py | 12 | 1.5 hours |
| coordinator.py | 14 | 2 hours |
| sensor.py | 19 | 1.5 hours |
| __init__.py | 6 | 45 mins |
| **TOTAL** | **64** | **~6 hours** |

---

## Success Metrics

Target coverage breakdown:
- **Statements**: 90%+
- **Branches**: 85%+ (complex branching in coordinator/sensor)
- **Functions**: 95%+
- **Lines**: 90%+

This will catch:
- ✅ Invalid input edge cases
- ✅ API error scenarios
- ✅ Timezone/parsing bugs
- ✅ Sensor calculation errors
- ✅ Integration lifecycle issues

---

## Next Steps

1. **Set up test infrastructure**
   - Create `tests/` directory
   - Add `conftest.py` with common fixtures
   - Add `pytest.ini` or `pyproject.toml` configuration

2. **Write tests in priority order**
   - Week 1: Validation & config flow
   - Week 2: Coordinator & sensors
   - Week 3: Integration & edge cases

3. **Add CI/CD integration**
   - GitHub Actions to run tests on PR
   - Fail if coverage drops below 85%

4. **Maintain tests**
   - Every new feature gets tests first (TDD)
   - Bug fixes include regression tests
