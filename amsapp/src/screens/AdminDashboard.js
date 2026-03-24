import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  RefreshControl, ActivityIndicator, Alert,
} from 'react-native';
import api from '../services/api';

const fmt = (iso) => {
  if (!iso) return '-';
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
};

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [msg, setMsg] = useState('');

  const load = useCallback(async () => {
    try {
      const res = await api.get('/api/admin/dashboard/');
      setData(res.data);
    } catch (e) { console.log(e); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const refresh = async () => { setRefreshing(true); await load(); setRefreshing(false); };

  const showMsg = (m) => { setMsg(m); setTimeout(() => setMsg(''), 3000); };

  const action = (pk, act) => {
    Alert.alert(
      act === 'approved' ? 'Approve' : 'Reject',
      'Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Yes',
          onPress: async () => {
            try {
              const res = await api.post(`/api/admin/leave/${pk}/${act}/`);
              showMsg(res.data.message);
              await load();
            } catch (e) { showMsg('Failed.'); }
          },
        },
      ]
    );
  };

  if (!data) return <View style={styles.loading}><ActivityIndicator size="large" color="#1e3a8a" /></View>;

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} />}
    >
      {!!msg && <View style={styles.msgBox}><Text style={styles.msgText}>{msg}</Text></View>}

      {/* Stats */}
      <View style={styles.statsRow}>
        <View style={styles.stat}>
          <Text style={styles.statNum}>{data.today_total}</Text>
          <Text style={styles.statLabel}>Total</Text>
        </View>
        <View style={styles.stat}>
          <Text style={[styles.statNum, { color: '#1e40af' }]}>{data.today_present}</Text>
          <Text style={styles.statLabel}>Present</Text>
        </View>
        <View style={styles.stat}>
          <Text style={[styles.statNum, { color: '#5b21b6' }]}>{data.today_wfh}</Text>
          <Text style={styles.statLabel}>WFH</Text>
        </View>
      </View>

      {/* Today Attendance */}
      <Text style={styles.sectionTitle}>Today's Attendance — {data.today}</Text>
      <View style={styles.card}>
        {data.today_attendance.length === 0 ? (
          <Text style={styles.empty}>No attendance marked yet.</Text>
        ) : data.today_attendance.map(a => (
          <View key={a.id} style={styles.row}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>{a.username.slice(0, 2).toUpperCase()}</Text>
            </View>
            <View style={{ flex: 1, marginLeft: 10 }}>
              <Text style={styles.username}>{a.username}</Text>
              {a.marked_at_str && <Text style={styles.muted}>{a.marked_at_str}</Text>}
            </View>
            <View style={[styles.badge, {
              backgroundColor: a.status === 'present' ? '#eff6ff' : '#f5f3ff'
            }]}>
              <Text style={{ fontSize: 11, fontWeight: '700', color: a.status === 'present' ? '#1e40af' : '#5b21b6' }}>
                {a.status.toUpperCase()}
              </Text>
            </View>
          </View>
        ))}
      </View>

      {/* Pending Leaves */}
      <Text style={styles.sectionTitle}>Pending Leave Requests ({data.pending_leaves.length})</Text>
      <View style={styles.card}>
        {data.pending_leaves.length === 0 ? (
          <Text style={styles.empty}>No pending requests.</Text>
        ) : data.pending_leaves.map(r => (
          <View key={r.id} style={styles.pendingRow}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>{r.username.slice(0, 2).toUpperCase()}</Text>
            </View>
            <View style={{ flex: 1, marginLeft: 10 }}>
              <Text style={styles.username}>{r.username}</Text>
              <Text style={styles.muted}>{fmt(r.start_date)} → {fmt(r.end_date)} · {r.num_days}d</Text>
              <Text style={styles.muted}>{r.reason}</Text>
            </View>
            <View style={styles.actionBtns}>
              <TouchableOpacity style={styles.approveBtn} onPress={() => action(r.id, 'approved')}>
                <Text style={styles.approveBtnText}>✓</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.rejectBtn} onPress={() => action(r.id, 'rejected')}>
                <Text style={styles.rejectBtnText}>✕</Text>
              </TouchableOpacity>
            </View>
          </View>
        ))}
      </View>

      {/* Leave History */}
      <Text style={styles.sectionTitle}>Leave History</Text>
      <View style={[styles.card, { marginBottom: 24 }]}>
        {data.done_leaves.length === 0 ? (
          <Text style={styles.empty}>No history yet.</Text>
        ) : data.done_leaves.map(r => (
          <View key={r.id} style={styles.row}>
            <View style={{ flex: 1 }}>
              <Text style={styles.username}>{r.username}</Text>
              <Text style={styles.muted}>{fmt(r.start_date)} → {fmt(r.end_date)} · {r.num_days}d</Text>
            </View>
            <View style={[styles.badge, {
              backgroundColor: r.status === 'approved' ? '#f0fdf4' : '#fef2f2'
            }]}>
              <Text style={{ fontSize: 11, fontWeight: '700', color: r.status === 'approved' ? '#15803d' : '#dc2626' }}>
                {r.status.toUpperCase()}
              </Text>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scroll: { flex: 1, backgroundColor: '#f5f7fb' },
  content: { padding: 16 },
  msgBox: { backgroundColor: '#f0fdf4', borderRadius: 8, padding: 10, marginBottom: 12, borderWidth: 1, borderColor: '#bbf7d0' },
  msgText: { color: '#15803d', fontWeight: '600', fontSize: 13 },
  statsRow: { flexDirection: 'row', gap: 10, marginBottom: 16 },
  stat: { flex: 1, backgroundColor: '#fff', borderRadius: 10, borderWidth: 1, borderColor: '#e2e8f0', padding: 14, alignItems: 'center' },
  statNum: { fontSize: 28, fontWeight: '800', color: '#0f172a' },
  statLabel: { fontSize: 10, fontWeight: '600', color: '#94a3b8', marginTop: 2 },
  sectionTitle: { fontSize: 13, fontWeight: '700', color: '#0f172a', marginBottom: 8 },
  card: { backgroundColor: '#fff', borderRadius: 10, borderWidth: 1, borderColor: '#e2e8f0', padding: 14, marginBottom: 14 },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#f1f5f9' },
  pendingRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#f1f5f9' },
  avatar: { width: 34, height: 34, borderRadius: 17, backgroundColor: '#eff6ff', justifyContent: 'center', alignItems: 'center' },
  avatarText: { fontSize: 11, fontWeight: '700', color: '#1e3a8a' },
  username: { fontSize: 13, fontWeight: '700', color: '#0f172a' },
  muted: { fontSize: 11, color: '#94a3b8', marginTop: 1 },
  badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  empty: { color: '#94a3b8', fontSize: 13, textAlign: 'center', padding: 16 },
  actionBtns: { flexDirection: 'row', gap: 6 },
  approveBtn: { backgroundColor: '#f0fdf4', borderWidth: 1, borderColor: '#bbf7d0', borderRadius: 6, width: 32, height: 32, justifyContent: 'center', alignItems: 'center' },
  approveBtnText: { color: '#15803d', fontWeight: '700', fontSize: 14 },
  rejectBtn: { backgroundColor: '#fef2f2', borderWidth: 1, borderColor: '#fecaca', borderRadius: 6, width: 32, height: 32, justifyContent: 'center', alignItems: 'center' },
  rejectBtnText: { color: '#dc2626', fontWeight: '700', fontSize: 14 },
});
