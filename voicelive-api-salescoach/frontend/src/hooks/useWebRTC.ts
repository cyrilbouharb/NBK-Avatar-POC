/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See LICENSE in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

import { useRef, useCallback, useEffect } from 'react'

export function useWebRTC(onSendOffer: (sdp: string) => void) {
  const pcRef = useRef<RTCPeerConnection | null>(null)
  const videoRef = useRef<HTMLVideoElement | null>(null)

  const setupWebRTC = useCallback(
    async (iceServers: any, username?: string, password?: string) => {
      let servers = Array.isArray(iceServers)
        ? iceServers
        : [{ urls: iceServers }]
      if (username && password) {
        servers = servers.map(s => ({
          urls: typeof s === 'string' ? s : s.urls,
          username,
          credential: password,
          credentialType: 'password' as const,
        }))
      }

      if (!servers?.length) {
        servers = [{ urls: 'stun:stun.l.google.com:19302' }]
      }

      const pc = new RTCPeerConnection({
        iceServers: servers,
        bundlePolicy: 'max-bundle',
      })

      let offerSent = false
      const sendLocalDescription = () => {
        if (offerSent || !pc.localDescription) return
        const payload = btoa(
          JSON.stringify({
            type: pc.localDescription.type,
            sdp: pc.localDescription.sdp,
          })
        )
        onSendOffer(payload)
        offerSent = true
      }

      const iceGatheringTimer = window.setTimeout(() => {
        sendLocalDescription()
      }, 2000)

      pc.onicecandidate = e => {
        if (!e.candidate) {
          window.clearTimeout(iceGatheringTimer)
          sendLocalDescription()
        }
      }

      pc.addEventListener('icegatheringstatechange', () => {
        if (pc.iceGatheringState === 'complete') {
          window.clearTimeout(iceGatheringTimer)
          sendLocalDescription()
        }
      })

      pc.ontrack = e => {
        if (e.track.kind === 'video' && videoRef.current) {
          videoRef.current.srcObject = e.streams[0]
          const playPromise = videoRef.current.play()
          if (playPromise) {
            void playPromise.catch(() => {})
          }
        } else if (e.track.kind === 'audio') {
          const audio = document.createElement('audio')
          audio.srcObject = e.streams[0]
          audio.autoplay = true
          audio.style.display = 'none'
          document.body.appendChild(audio)
        }
      }

      pc.addTransceiver('video', { direction: 'recvonly' })
      pc.addTransceiver('audio', { direction: 'recvonly' })

      const offer = await pc.createOffer()
      await pc.setLocalDescription(offer)

      if (pc.iceGatheringState === 'complete') {
        window.clearTimeout(iceGatheringTimer)
        sendLocalDescription()
      }

      pcRef.current = pc
    },
    [onSendOffer]
  )

  const handleAnswer = useCallback(async (msg: any) => {
    if (!pcRef.current || pcRef.current.signalingState !== 'have-local-offer')
      return

    const sdp = msg.server_sdp
      ? JSON.parse(atob(msg.server_sdp)).sdp
      : msg.sdp || msg.answer

    if (sdp) {
      await pcRef.current.setRemoteDescription({ type: 'answer', sdp })
    }
  }, [])

  useEffect(() => {
    return () => {
      pcRef.current?.close()
    }
  }, [])

  return {
    setupWebRTC,
    handleAnswer,
    videoRef,
  }
}
