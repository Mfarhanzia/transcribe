import moviepy.editor as mp
from moviepy.editor import *
import speech_recognition as sr


def slow_down_video(factor=1):
    video_clip = VideoFileClip("./video.mp4")
    slowed_down_clip = video_clip.fx(vfx.speedx, factor)
    slowed_down_clip.write_videofile("./video_slow.mp4")


def video_to_audio(video_path=None, audio_path=None):
    video_path = "./video_slow.mp4"
    audio_path = "./audio.wav"
    clip = mp.VideoFileClip(video_path).subclip(0,40)
    clip.audio.write_audiofile(audio_path)
    return True


def audio_to_text():
    print(sr.__version__)
    src_wav = "./audio.wav"

    r = sr.Recognizer()
    file_audio = sr.AudioFile(src_wav)

    with file_audio as source:
        audio_text = r.record(source)

    print(type(audio_text))
    text = r.recognize_google(audio_text)
    print(text)
    output_file = "./output_text.txt"
    with open(output_file, "w") as file:
        file.write(text)
    return text


def transcribe_wav_to_text():
    wav_file = "./audio.wav"
    recognizer = sr.Recognizer()

    with sr.AudioFile(wav_file) as source:
        recognizer.adjust_for_ambient_noise(source)

        audio_data = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio_data)
            output_file = "./output_text2.txt"
            with open(output_file, "w") as file:
                file.write(text)
        except sr.UnknownValueError:
            print("Google Web Speech API could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Web Speech API; {e}")


if __name__ == "__main__":
    slow_down_video()
    video_to_audio()
    # audio_to_text()
    transcribe_wav_to_text()




"""
helpers

import whisper
import moviepy.editor as mp



def video_to_audio(video_path, audio_path):
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    return True


def get_text_from_audio(audio_path):
    if not audio_path:
        audio_path = "./audio.wav"

    model = whisper.load_model("base")
    
    result = model.transcribe(audio_path)
    return result["text"]
"""

"""
topic_assets.py

from django.core.files.storage import FileSystemStorage
from spekit.helpers import video_to_audio, get_text_from_audio


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def updated_media_file(request, *args, **kwargs):
    file  = request.FILES.get("file")
    if not file:
        return Response({"success": False})
    fs = FileSystemStorage()
    file_name = f"{request.user.id}_{file.name}"
    fs.save(file_name, file)
    
    video_path = f"{fs.location}/{file_name}"
    audio_path = f"{fs.location}/{request.user.id}_audio.wav"
    
    video_to_audio(video_path, audio_path)
    text = get_text_from_audio(audio_path)
    
    data = {
        "transcribed_text": text,
        "success": True,
    }
    return Response(data)

path("upload_transcribe_file", topic_assets.updated_media_file, name="upload-transcribe-file"),
    
"""

"""
import React, {useState, useRef} from 'react';

import {
  EncapsulatedInput,
  VStack,
  EmbeddedSpekPopover,
  DSButton as Button,
  Heading,
  Icon,
  HStack,
  Divider,
  ActionWithConfirmation,
  Link,
  DSTooltip as Tooltip,
  Box,
  useToast,
  Grid,
  PrivacySettings,
  Button as ClickButton,
} from 'spekit-ui';
import {RiQuestionLine, RiCloseLine, RiAddCircleLine} from 'react-icons/ri';
import {
  CKE_CONTENT_SIZE_ERROR,
  CONTENT_SHARING,
  fetchMiddleWare,
  getSearchParam,
  logging,
  topics as topicsAPI,
  utils,
} from 'spekit-datalayer';
import {
  ISpekFromState,
  TClonedTerm,
  ICreateSpekResponse,
  IPerson,
  TCreateSpekPayload,
  IExtendedNotificationState,
  IOptionType,
} from 'spekit-types';
import {EditingView, EditingViewProps} from '../../RichTextEditor/components/EditingView';
import {getFormValues, resolver} from './form';
import {FormProvider, useForm, Controller} from 'react-hook-form';
import {TopicPicker} from '../TopicPicker';
import {ExpertPicker} from '../ExpertPicker';
import {spekAPI} from 'spekit-datalayer';
import {SalesforceObjectPicker} from '../SalesforceObjectPicker';
import {useAI} from '../../hooks/useAI';

import {ReactComponent as SmartTitleIcon} from '../../spekitAI/ai_sparkle.svg';
import {ReactComponent as SmartTitleIconAnim} from '../../spekitAI/ai_sparkle_anim.svg';
import {CustomFieldsEditor} from '../../Content/CustomFieldsEditor/CustomFieldsEditor';
import {SaveButton} from '../../Content/ContentPresenter/SaveButton';

const fetch = fetchMiddleWare.fetchMiddleWare;

export interface SpekFormProps extends EditingViewProps {
  onClose: () => void;
  openSpotlightModal: (props: any) => void;
  termToClone?: TClonedTerm;
  onSave?: (
    state: ICreateSpekResponse,
    createSpotlight: boolean,
    notificationSettings: {
      sendNotification: boolean;
      sendEmail: boolean;
      message: string;
      teams: IOptionType[];
    }
  ) => void;
  hasSpekitAI?: boolean;
  user?: IPerson; // for setting default data expert
  hasSpekSharing?: boolean;
  spekID?: string;
  hasCustomFields?: boolean;
  hasSpekLinkGeneration?: boolean;
}

export default function SpekForm({
  placeholder,
  host,
  onClose,
  openSpotlightModal,
  termToClone,
  onSave,
  hasSpekitAI,
  hasSpekSharing,
  hasSpekLinkGeneration,
  user,
  spekID,
  hasCustomFields,
}: SpekFormProps) {
  // if we are cloning a term, we need to populate the form with the values of the term
  const methods = useForm<ISpekFromState>({
    defaultValues: getFormValues({termToClone, user, hasSpekSharing}),
    resolver,
    mode: 'onChange',
  });

  const {setValue, control, watch, setError, getValues, handleSubmit} = methods;

  // uploading state to disable the submit button
  const [isUploading, setIsUploading] = useState(false);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const {generateTitle, processing} = useAI();
  const [transcribeFile, setTranscribeFile] = useState<File | undefined>(undefined);
  const [isVideoTextProcessing, setIsVideoTextProcessing] = useState(false);
  const [definitionValue, setDefinitionValue] = useState('');

  // toast for messages
  const toast = useToast();

  const getNewTitle = async (content: string) => {
    const response = await generateTitle(content, spekID || '');
    if (response) {
      setValue('title', response);
    } else {
      toast({
        variant: 'error',
        description: 'Request unsuccessful. Please try again.',
      });
    }
  };

  // watch for changes to the notification checkbox and topics
  const tags = watch('topics');
  const customFields = watch('customFields');
  const definition = watch('definition');

  React.useEffect(() => {
    const isCloning = Boolean(termToClone?.id);
    if (isCloning) return;
    async function initializeTopic() {
      const search = await getSearchParam();
      const {topic: topicId, tag: topicName} = utils.parseQs(search) as Partial<{
        topic: string;
        tag: string;
      }>;
      const topics = await topicsAPI.get(topicName, {allowedOnly: true});
      const topic = topics.find((topic) => topic.value === topicId);
      if (topic) setValue('topics', [topic]);
    }
    initializeTopic();
  }, [setValue, termToClone?.id]);

  // save the form state to the database
  // open create spotlight modal if the user has selected that option
  const onCreate = async (notification: IExtendedNotificationState) => {
    setIsFormProcessing(true);
    const {notifyByEmail, sendNotification, message, createSpotlight, teams} =
      notification;
    const state = getValues();
    try {
      const spekPayload: TCreateSpekPayload = {
        ...state,
        notification,
      };
      const response = await spekAPI.createSpek(spekPayload);
      const toastMessage = sendNotification
        ? 'Spek created and users notified!'
        : 'Spek created!';
      if (response) {
        // onSave is a function passed by the webapp or extension to handle the response.
        // Each environment has unique needs
        if (onSave)
          onSave(response, createSpotlight, {
            sendNotification,
            sendEmail: notifyByEmail,
            message,
            teams,
          });
        //@TODO add tracking
        toast({description: toastMessage, variant: 'success'});
        // webapp only - no host
        if (createSpotlight && !host) {
          openSpotlightModal({
            isSpotlightSelected: true,
            businessTerm: response.business_term,
            message,
            teams,
          });
        }
        onClose();
      }
    } catch (e) {
      logging.capture(e);
      if (e.message === 'Payload too large') {
        setError('definition', {
          type: 'manual',
          message: CKE_CONTENT_SIZE_ERROR,
        });
      }
    } finally {
      setIsFormProcessing(false);
    }
  };

  const videoToTextFileRef = useRef<HTMLInputElement | null>(null);

  const handleTranscribeFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    setTranscribeFile(selectedFile);
  };

  const getVideoText = async () => {
    if (!transcribeFile){
      toast({
        variant: 'error',
        description: 'Upload file to get text.',
      });
      return
    }
    setIsVideoTextProcessing(true);
    const formData = new FormData();
    formData.append('file', transcribeFile, transcribeFile.name);
    const response: any = await fetch(`/api/v1/upload_transcribe_file`, {
      // credentials: 'include',
      method: 'post',
      body: formData,
    });

    let result = await response.json();

    if (result.success === true){
      setDefinitionValue(result.transcribed_text);
      setTranscribeFile(undefined)
      if (videoToTextFileRef.current){
        videoToTextFileRef.current.value = ''
        videoToTextFileRef.current.type = "text";
        videoToTextFileRef.current.type = "file";
      }
    } 
    setIsVideoTextProcessing(false);
  };

  return (
    <FormProvider {...methods}>
      <Grid
        // height hack for consistent scrolling experience in extension iframe
        height={host ? '100vh' : 'auto'}
        gridTemplateColumns={'1fr'}
        gridTemplateRows={'min-content 1fr min-content'}
        minH={0}
      >
        {/* design requirements require some hacky padding here */}
        <HStack
          justifyContent='space-between'
          alignItems='center'
          boxSizing={'border-box'}
          marginLeft={'-1px'}
          // required for differences in extension rendering
          // temporary until modal is phased out
          pl={host ? '4px' : '0px'}
          width={host ? 'calc(100% - 4px)' : 'calc(100% + 12px)'}
        >
          <Heading fontSize='large' fontWeight='semibold'>
            Create Spek
          </Heading>
          <HStack>
            <Tooltip label='Help center' placement='bottom' shouldWrapChildren>
              <Button
                as={Link}
                icon={<Icon h='1.2rem' w='1.2rem' as={RiQuestionLine} />}
                aria-label='Help Center Link'
                colorScheme='white'
                variant='icon'
                size='medium'
                isExternal
                href='https://help.spekit.com/hc/en-us/articles/9922580438299-How-do-I-create-Speks-'
              />
            </Tooltip>
            <SaveButton
              topics={tags.map((t) => t.value)}
              mode='create'
              handleSubmit={handleSubmit}
              onSave={onCreate}
              isSubmitting={isFormProcessing}
              disabled={isUploading || isFormProcessing}
              testId='create-spek-button'
            />
            <Divider orientation='vertical' h='2rem' />
            <ActionWithConfirmation
              icon={RiCloseLine}
              confirmationHeader='Close this Spek'
              confirmationMessage='Are you sure? Closing this Spek will cause your progress to be deleted.'
              confirmActionText='Yes, close'
              confirmAction={onClose}
              actionTooltip='Close'
            />
          </HStack>
        </HStack>
        {/* the margins and scrollbar are here to match with the extension as we prepare to migrate from the modal */}
        <Box
          id='spek-creation-modal'
          data-testid='spekCreation-modal'
          overflowY={'auto'}
          mt={10}
          pr={'8px'}
          pl={'4px'}
          boxSizing='border-box'
          // required for differences in extension rendering
          // will be removed when modal is phased out
          marginRight={host ? 0 : '-16px'}
          marginLeft={host ? 0 : '-4px'}
          sx={{
            // match scrollbar to extension
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-thumb': {
              background: '#d8dbe0',
              borderRadius: '2px',
            },
          }}
        >
          <VStack alignItems='start' width='100%' pb={3} data-testid='spekCreation-modal'>
            <Controller
              name='title'
              control={control}
              render={({field, fieldState}) => (
                <EncapsulatedInput
                  {...field}
                  testId='spek-title-input'
                  label='Spek title'
                  isRequired
                  placeholder='Enter Spek title'
                  helpText={<EmbeddedSpekPopover />}
                  errorMessage={fieldState.error?.message}
                  isInvalid={!!fieldState.error}
                  isDisabled={processing}
                  inputControl={
                    hasSpekitAI && (
                      <Tooltip label='Smart Title' placement='top' shouldWrapChildren>
                        <Button
                          icon={
                            <Icon
                              h='1.2rem'
                              w='1.2rem'
                              as={processing ? SmartTitleIconAnim : SmartTitleIcon}
                            />
                          }
                          aria-label='Smart Title Button'
                          data-testid='smart-title-button'
                          colorScheme='outlined'
                          variant='icon'
                          size='medium'
                          onClick={() => getNewTitle(getValues('definition'))}
                          isDisabled={processing || definition === ''}
                        />
                      </Tooltip>
                    )
                  }
                />
              )}
            />
            <Controller
              name='definition'
              control={control}
              render={({field, fieldState}) => (
                <EditingView
                  {...field}
                  value={definitionValue}
                  placeholder={placeholder}
                  host={host}
                  uploadHandler={fetch}
                  setUploadBusy={() => setIsUploading(true)}
                  unSetUploadBusy={() => setIsUploading(false)}
                  enhanced={hasSpekitAI}
                  spekID={spekID}
                  isError={!!fieldState.error}
                  errorMessage={fieldState.error?.message}
                />
              )}
            />
            <VStack alignItems='start' width='100%'>
            <HStack alignItems='start' width='100%'>
                <Box maxW='500px' width='100%'>
                  <input
                    ref={videoToTextFileRef}
                    name='video-to-text-file'
                    type='file'
                    accept='video/mp4,video/x-m4v,video/*'
                    onChange={handleTranscribeFileChange}
                  />
                </Box>
                <Box maxW='500px' width='100%'>
                  <ClickButton
                    colorScheme='primary'
                    onClick={getVideoText}
                    disabled={isVideoTextProcessing}
                  >
                    {isVideoTextProcessing ? 'Loading...' : 'Get Text'}
                  </ClickButton>
                </Box>
              </HStack>
              <HStack alignItems='start' width='100%'>
                {/* all of the inputs have a matching width, but the topic picker has a button to the right.
              we wrap all the inputs to give them consistent width while allowing space for a button */}
                <Box maxW='500px' width='100%'>
                  <TopicPicker />
                </Box>
                <Button
                  href={`${host || ''}/app/wiki/topics/create`}
                  as={Link}
                  colorScheme='primary'
                  leftIcon={<Icon h='18px' w='18px' as={RiAddCircleLine} />}
                  size='large'
                  variant='ghost'
                  target='_blank'
                  // this margin aligns the button with the topic picker
                  mt={'33px !important'}
                >
                  Create Topic
                </Button>
              </HStack>
              <Box maxW='500px' width='100%'>
                <ExpertPicker tags={tags.map((t) => t.label)} />
              </Box>
              <Box maxW='500px' width='100%'>
                <SalesforceObjectPicker />
              </Box>
              {hasCustomFields && (
                <Box w='500px'>
                  <Box mt={16}>
                    <CustomFieldsEditor
                      type={'business_term'}
                      updateValues={(customFields) =>
                        setValue('customFields', customFields)
                      }
                      values={customFields}
                    />
                  </Box>
                </Box>
              )}
              {hasSpekSharing && (
                <Controller
                  name='shareable'
                  control={control}
                  render={({field}) => (
                    <Box mt='24px !important'>
                      <PrivacySettings
                        data-testid='spek-external-share-control'
                        isChecked={field.value}
                        onChange={field.onChange}
                      >
                        {hasSpekLinkGeneration
                          ? CONTENT_SHARING.ALL_USERS
                          : CONTENT_SHARING.EXPERTS_AND_ADMINS}
                      </PrivacySettings>
                    </Box>
                  )}
                />
              )}
            </VStack>
          </VStack>
        </Box>
      </Grid>
    </FormProvider>
  );
}

"""