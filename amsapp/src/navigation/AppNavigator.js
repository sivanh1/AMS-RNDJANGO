import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../services/AuthContext';

import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import UserDashboard from '../screens/UserDashboard';
import AdminDashboard from '../screens/AdminDashboard';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function UserTabs({ user, logout }) {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => (
          <Ionicons name={focused ? 'home' : 'home-outline'} size={size} color={color} />
        ),
        tabBarActiveTintColor: '#1e3a8a',
        tabBarInactiveTintColor: '#94a3b8',
        headerStyle: { backgroundColor: '#1e3a8a' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: '700' },
        headerRight: () => (
          <TouchableOpacity onPress={logout} style={{ paddingRight: 16 }}>
            <Ionicons name="log-out-outline" size={20} color="#fff" />
          </TouchableOpacity>
        ),
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={UserDashboard}
        options={{ title: 'My Dashboard', tabBarLabel: 'Dashboard' }}
      />
    </Tab.Navigator>
  );
}

function AdminTabs({ user, logout }) {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => (
          <Ionicons name={focused ? 'grid' : 'grid-outline'} size={size} color={color} />
        ),
        tabBarActiveTintColor: '#1e3a8a',
        tabBarInactiveTintColor: '#94a3b8',
        headerStyle: { backgroundColor: '#1e3a8a' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: '700' },
        headerRight: () => (
          <TouchableOpacity onPress={logout} style={{ paddingRight: 16 }}>
            <Ionicons name="log-out-outline" size={20} color="#fff" />
          </TouchableOpacity>
        ),
      })}
    >
      <Tab.Screen
        name="AdminDash"
        component={AdminDashboard}
        options={{ title: 'Admin Dashboard', tabBarLabel: 'Dashboard' }}
      />
    </Tab.Navigator>
  );
}

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}

export default function AppNavigator() {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return (
      <View style={styles.splash}>
        <Text style={styles.splashText}>AMS</Text>
        <ActivityIndicator color="rgba(255,255,255,0.6)" style={{ marginTop: 16 }} />
      </View>
    );
  }

  return (
    <NavigationContainer>
      {!user ? (
        <AuthStack />
      ) : user.is_staff ? (
        <AdminTabs user={user} logout={logout} />
      ) : (
        <UserTabs user={user} logout={logout} />
      )}
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  splash: { flex: 1, backgroundColor: '#1e3a8a', justifyContent: 'center', alignItems: 'center' },
  splashText: { fontSize: 40, fontWeight: '800', color: '#fff' },
});
