use std::{
    cell::RefCell,
    cmp::Ordering,
    collections::HashMap,
    fmt::{Display, Formatter},
    hash::Hasher,
    rc::Rc,
};

use serde::{Deserialize, Serialize};
use smol_str::SmolStr;

use picodata_plugin::system::tarantool::{
    self, datetime::Datetime, decimal::Decimal, tlua, tuple::FieldType, tuple::KeyDefPart,
    uuid::Uuid,
};

thread_local! {
    pub static LOCAL_BUCKETS: Rc<RefCell<HashMap<BucketId, SmolStr>>> = Rc::new(RefCell::new(HashMap::with_capacity(3000)));
}

type BucketId = u64;

#[derive(Default, Debug, Serialize, Deserialize, tlua::LuaRead)]
struct OnBucketEventData {
    pub spaces: Vec<String>,
}

#[derive(Debug)]
enum BucketEvent {
    /// The space data was moved to another replicaset and is now
    /// being garbage collected
    GarbageCollection,
    /// The space data was moved to this replicaset
    Received,
}

impl From<String> for BucketEvent {
    fn from(value: String) -> Self {
        match value.as_str() {
            "bucket_data_gc_txn" => Self::GarbageCollection,
            "bucket_data_recv_txn" => Self::Received,
            _ => unreachable!("there is no other bucket events"),
        }
    }
}

pub fn set_bucket_event_listener() {
    let state = tarantool::lua_state();

    state.set("_pind_on_bucket_event_fn", {
        let bucket_clone = LOCAL_BUCKETS.with(std::clone::Clone::clone);

        tarantool::tlua::function3(
            move |event: String, bucket_id: BucketId, data: OnBucketEventData| {
                let event = BucketEvent::from(event);

                // match event {
                //     BucketEvent::GarbageCollection => todo!("remove from index"),
                //     BucketEvent::Received => todo!("add to index"),
                // }

                let mut lock = bucket_clone.borrow_mut();
                // TODO: get all indexes that are built on data.spaces and update them
                log::debug!(
                    "got event {event:?}, at bucket_id = {bucket_id}, with data = {data:?}"
                );
                lock.remove(&bucket_id);
            },
        )
    });

    state
        .eval::<()>("vshard.storage.on_bucket_event(_pind_on_bucket_event_fn)")
        .expect("setting vshard callback shouldn't fail");
}

#[allow(dead_code)]
// Copied from picodata: https://git.picodata.io/core/picodata/-/blob/25.1/src/sql/router.rs?ref_type=heads#L332
pub(crate) fn calculate_bucket_id(tuple: &[&Value], bucket_count: u64) -> BucketId {
    let tnt_tuple = tarantool::tuple::Tuple::new(tuple)
        .inspect_err(|e| {
            // TODO: map error
            log::error!("got error constructing tuple: {e:?}");
        })
        .unwrap();
    let mut key_parts = Vec::with_capacity(tuple.len());
    for (pos, value) in tuple.iter().enumerate() {
        let pos = u32::try_from(pos).expect("the tuple for calculating bucket_id is too long");
        key_parts.push(value.as_key_def_part(pos));
    }

    let key = tarantool::tuple::KeyDef::new(key_parts.as_slice())
        .inspect_err(|e| {
            log::error!("failed to create keydef of a tuple {tuple:?}: {e}");
        })
        .unwrap();
    (u64::from(key.hash(&tnt_tuple)) % bucket_count + 1)
}

#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
#[serde(transparent)]
pub struct Double {
    pub value: f64,
}

impl Eq for Double {}

impl PartialOrd for Double {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Double {
    fn cmp(&self, other: &Self) -> Ordering {
        let self_value = self.value;
        let other_value = other.value;
        let is_special = |f: f64| f.is_nan() || f.is_infinite();
        let self_is_special = is_special(self_value);
        let other_is_special = is_special(other_value);

        if self_is_special {
            if self_value.is_nan() {
                if other_value.is_nan() {
                    Ordering::Equal
                } else {
                    Ordering::Greater
                }
            } else if self_value == f64::INFINITY {
                if other_value.is_nan() {
                    Ordering::Less
                } else if other_value == f64::INFINITY {
                    Ordering::Equal
                } else {
                    Ordering::Greater
                }
            } else if other_value == f64::NEG_INFINITY {
                Ordering::Equal
            } else {
                Ordering::Less
            }
        } else if other_is_special {
            if other_value == f64::NEG_INFINITY {
                Ordering::Greater
            } else {
                Ordering::Less
            }
        } else {
            let self_decimal = Decimal::try_from(self_value).unwrap();
            let other_decimal = Decimal::try_from(other_value).unwrap();
            self_decimal.cmp(&other_decimal)
        }
    }
}

#[allow(clippy::derived_hash_with_manual_eq)]
impl std::hash::Hash for Double {
    /// We get hash from the internal float64 bit representation.
    /// As a side effect, `hash(NaN) == hash(NaN)` is true. We
    /// should manually care about this case in the code.
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.value.to_bits().hash(state);
    }
}

impl Display for Double {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "{}", self.value)
    }
}

/// Values are used to keep constants in the IR tree
/// or results in the virtual tables.
#[derive(Hash, PartialEq, Debug, Default, Clone, Deserialize, Serialize, PartialOrd, Ord)]
pub enum Value {
    /// Boolean type.
    Boolean(bool),
    /// Fixed point type.
    /// Box here to make the size of Value 32 bytes
    Decimal(Box<Decimal>),
    /// Floating point type.
    Double(Double),
    /// Datetime type,
    Datetime(Datetime),
    /// Signed integer type.
    Integer(i64),
    /// SQL NULL ("unknown" in the terms of three-valued logic).
    #[default]
    Null,
    /// String type.
    String(String),
    /// Tuple type
    Tuple(Vec<Value>),
    /// Uuid type
    Uuid(Uuid),
}

/// As a side effect, `NaN == NaN` is true.
/// We should manually care about this case in the code.
impl Eq for Value {}

impl Display for Value {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        match self {
            Value::Boolean(v) => write!(f, "{v}"),
            Value::Null => write!(f, "NULL"),
            Value::Integer(v) => write!(f, "{v}"),
            Value::Datetime(v) => write!(f, "'{v}'"),
            Value::Double(v) => Display::fmt(&v, f),
            Value::Decimal(v) => Display::fmt(v, f),
            Value::String(v) => write!(f, "'{v}'"),
            Value::Tuple(v) => write!(f, "{v:?}"),
            Value::Uuid(v) => Display::fmt(v, f),
        }
    }
}

impl Value {
    #[must_use]
    pub fn as_key_def_part(&self, field_no: u32) -> KeyDefPart<'_> {
        let field_type = match self {
            Value::Boolean(_) => FieldType::Boolean,
            Value::Integer(_) => FieldType::Integer,
            Value::Datetime(_) => FieldType::Datetime,
            Value::Decimal(_) => FieldType::Decimal,
            Value::Double(_) => FieldType::Double,
            Value::String(_) => FieldType::String,
            Value::Tuple(_) => FieldType::Array,
            Value::Uuid(_) => FieldType::Uuid,
            Value::Null => FieldType::Any,
        };
        KeyDefPart {
            field_no,
            field_type,
            collation: None,
            is_nullable: true,
            path: None,
        }
    }
}
