import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { useAuth } from '../services/AuthContext';

import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import UserDashboard from '../screens/UserDashboard';
import ApplyWFH from '../screens/ApplyWFH';
import RequestHistory from '../screens/RequestHistory';
import AdminDashboard from '../screens/AdminDashboard';
import AdminWFH from '../screens/AdminWFH';
import ApiConfigScreen from '../screens/ApiConfigScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const headerOpts = (logout) => ({
  headerStyle: { backgroundColor: '#1e3a8a' },
  headerTintColor: '#fff',
  headerTitleStyle: { fontWeight: '700' },
  headerRight: () => (
    <TouchableOpacity onPress={logout} style={{ paddingRight: 16 }}>
      <Ionicons name="log-out-outline" size={20} color="#fff" />
    </TouchableOpacity>
  ),
});

const tabIcon = {
  Dashboard:  { on: 'home',       off: 'home-outline' },
  WFH:        { on: 'laptop',     off: 'laptop-outline' },
  History:    { on: 'time',       off: 'time-outline' },
  AdminDash:  { on: 'grid',       off: 'grid-outline' },
  AdminWFH:   { on: 'people',     off: 'people-outline' },
};

function UserTabs({ logout }) {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons = tabIcon[route.name] || tabIcon.Dashboard;
          return <Ionicons name={focused ? icons.on : icons.off} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#1e3a8a',
        tabBarInactiveTintColor: '#94a3b8',
        ...headerOpts(logout),
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={UserDashboard}
        options={{ title: 'My Dashboard' }}
      />
      <Tab.Screen
        name="WFH"
        component={ApplyWFH}
        options={{ title: 'Apply WFH' }}
      />
      <Tab.Screen
        name="History"
        component={RequestHistory}
        options={{ title: 'Request History' }}
      />
    </Tab.Navigator>
  );
}

function AdminTabs({ logout }) {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons = tabIcon[route.name] || tabIcon.AdminDash;
          return <Ionicons name={focused ? icons.on : icons.off} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#1e3a8a',
        tabBarInactiveTintColor: '#94a3b8',
        ...headerOpts(logout),
      })}
    >
      <Tab.Screen
        name="AdminWFH"
        component={AdminWFH}
        options={{ title: 'WFH Requests' }}
      />
    </Tab.Navigator>
  );
}

function AuthStack({ initialRoute }) {
  return (
    <Stack.Navigator initialRouteName={initialRoute} screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ApiConfig" component={ApiConfigScreen} />
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}

export default function AppNavigator() {
  const { user, loading, logout } = useAuth();

  const [checkingApi, setCheckingApi] = useState(true);
  const [initialRoute, setInitialRoute] = useState("Login");

  useEffect(() => {
    const checkApi = async () => {
      try {
        const apiUrl = await AsyncStorage.getItem('API_URL');

        if (!apiUrl) {
          setInitialRoute("ApiConfig");
        } else {
          setInitialRoute("Login");
        }
      } catch (error) {
        console.log("Error checking API URL:", error);
        setInitialRoute("ApiConfig");
      } finally {
        setCheckingApi(false);
      }
    };

    checkApi();
  }, []);

  if (loading || checkingApi) {
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
        <AuthStack initialRoute={initialRoute} />
      ) : user.is_staff ? (
        <AdminTabs logout={logout} />
      ) : (
        <UserTabs logout={logout} />
      )}
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  splash: {
    flex: 1,
    backgroundColor: '#1e3a8a',
    justifyContent: 'center',
    alignItems: 'center'
  },
  splashText: {
    fontSize: 40,
    fontWeight: '800',
    color: '#fff'
  },
});